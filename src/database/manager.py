#!/usr/bin/env python3
"""
SEC报告数据库管理器

支持SQLite、PostgreSQL和MySQL的统一接口
提供连接管理、会话处理和数据库操作的高级封装
"""

import os
import sys
from typing import Optional, Dict, Any, List, Union
from urllib.parse import urlparse
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.database.models import Base, Company, ReportType, ReportSection, Metric, FinancialData, InvalidMetricCache, DataFetchLog

# 配置日志
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """数据库配置类"""
    
    # 默认SQLite配置
    SQLITE_DEFAULT = {
        'path': os.path.join(os.path.dirname(__file__), '../../data/sec_reports.db'),
        'echo': False,
        'pool_pre_ping': True
    }
    
    # PostgreSQL配置模板
    POSTGRESQL_TEMPLATE = {
        'host': 'localhost',
        'port': 5432,
        'database': 'sec_reports',
        'username': 'sec_user',
        'password': 'sec_password',
        'echo': False,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # MySQL配置模板
    MYSQL_TEMPLATE = {
        'host': 'localhost',
        'port': 3306,
        'database': 'sec_reports',
        'username': 'sec_user',
        'password': 'sec_password',
        'charset': 'utf8mb4',
        'echo': False,
        'pool_size': 10,
        'max_overflow': 20
    }


class DatabaseManager:
    """数据库管理器 - 支持多种数据库后端"""
    
    def __init__(self, database_url: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        初始化数据库管理器
        
        Args:
            database_url: 数据库连接URL，如果提供则优先使用
            config: 数据库配置字典
        """
        self.engine: Optional[Engine] = None
        self.Session: Optional[sessionmaker] = None
        self.database_url = database_url
        self.config = config or {}
        self.db_type = None
        
        # 如果提供了URL，从URL中解析数据库类型
        if database_url:
            parsed = urlparse(database_url)
            self.db_type = parsed.scheme.split('+')[0]  # 处理如 postgresql+psycopg2 的情况
        
        logger.info(f"DatabaseManager initialized with db_type: {self.db_type}")
    
    def connect(self) -> bool:
        """
        连接数据库
        
        Returns:
            连接是否成功
        """
        try:
            if self.database_url:
                # 使用提供的URL
                self.engine = self._create_engine_from_url(self.database_url)
            else:
                # 根据配置创建引擎
                self.engine = self._create_engine_from_config()
            
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # 创建会话工厂
            self.Session = sessionmaker(bind=self.engine)
            
            logger.info(f"Successfully connected to {self.db_type} database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def _create_engine_from_url(self, url: str) -> Engine:
        """从URL创建数据库引擎"""
        parsed = urlparse(url)
        self.db_type = parsed.scheme.split('+')[0]
        
        engine_kwargs = {
            'echo': self.config.get('echo', False),
            'pool_pre_ping': True
        }
        
        # 根据数据库类型设置特定参数
        if self.db_type == 'sqlite':
            # SQLite特定设置
            engine_kwargs['connect_args'] = {'check_same_thread': False}
        elif self.db_type in ['postgresql', 'mysql']:
            # PostgreSQL和MySQL的连接池设置
            engine_kwargs.update({
                'pool_size': self.config.get('pool_size', 10),
                'max_overflow': self.config.get('max_overflow', 20),
                'pool_recycle': 3600
            })
        
        return create_engine(url, **engine_kwargs)
    
    def _create_engine_from_config(self) -> Engine:
        """从配置创建数据库引擎"""
        # 默认使用SQLite
        if not self.config or not self.config.get('type'):
            return self._create_sqlite_engine()
        
        db_type = self.config.get('type', 'sqlite').lower()
        self.db_type = db_type
        
        if db_type == 'sqlite':
            return self._create_sqlite_engine()
        elif db_type == 'postgresql':
            return self._create_postgresql_engine()
        elif db_type == 'mysql':
            return self._create_mysql_engine()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _create_sqlite_engine(self) -> Engine:
        """创建SQLite引擎"""
        db_path = self.config.get('path', DatabaseConfig.SQLITE_DEFAULT['path'])
        
        # 确保数据库目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        url = f"sqlite:///{db_path}"
        
        return create_engine(
            url,
            echo=self.config.get('echo', False),
            pool_pre_ping=True,
            connect_args={'check_same_thread': False}
        )
    
    def _create_postgresql_engine(self) -> Engine:
        """创建PostgreSQL引擎"""
        config = {**DatabaseConfig.POSTGRESQL_TEMPLATE, **self.config}
        
        url = (f"postgresql://{config['username']}:{config['password']}"
               f"@{config['host']}:{config['port']}/{config['database']}")
        
        return create_engine(
            url,
            echo=config.get('echo', False),
            pool_size=config.get('pool_size', 10),
            max_overflow=config.get('max_overflow', 20),
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def _create_mysql_engine(self) -> Engine:
        """创建MySQL引擎"""
        config = {**DatabaseConfig.MYSQL_TEMPLATE, **self.config}
        
        url = (f"mysql+pymysql://{config['username']}:{config['password']}"
               f"@{config['host']}:{config['port']}/{config['database']}"
               f"?charset={config.get('charset', 'utf8mb4')}")
        
        return create_engine(
            url,
            echo=config.get('echo', False),
            pool_size=config.get('pool_size', 10),
            max_overflow=config.get('max_overflow', 20),
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def create_tables(self) -> bool:
        """
        创建所有数据库表
        
        Returns:
            创建是否成功
        """
        try:
            if not self.engine:
                raise RuntimeError("Database not connected")
            
            Base.metadata.create_all(self.engine)
            logger.info("All database tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def drop_tables(self) -> bool:
        """
        删除所有数据库表
        
        Returns:
            删除是否成功
        """
        try:
            if not self.engine:
                raise RuntimeError("Database not connected")
            
            Base.metadata.drop_all(self.engine)
            logger.info("All database tables dropped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            return False
    
    def get_session(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            SQLAlchemy会话对象
        """
        if not self.Session:
            raise RuntimeError("Database not connected")
        
        return self.Session()
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """
        执行原生SQL语句
        
        Args:
            sql: SQL语句
            params: 参数字典
            
        Returns:
            查询结果
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                if sql.strip().upper().startswith('SELECT'):
                    return result.fetchall()
                else:
                    conn.commit()
                    return result.rowcount
                    
        except Exception as e:
            logger.error(f"Failed to execute SQL: {e}")
            raise
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Returns:
            数据库信息字典
        """
        if not self.engine:
            return {'status': 'disconnected'}
        
        try:
            with self.get_session() as session:
                # 获取表统计信息
                table_stats = {}
                
                # 统计各表记录数
                models = [Company, ReportType, ReportSection, Metric, FinancialData, InvalidMetricCache, DataFetchLog]
                for model in models:
                    count = session.query(model).count()
                    table_stats[model.__tablename__] = count
                
                return {
                    'status': 'connected',
                    'database_type': self.db_type,
                    'engine_url': str(self.engine.url).replace(str(self.engine.url.password), '***') if self.engine.url.password else str(self.engine.url),
                    'table_statistics': table_stats,
                    'pool_size': getattr(self.engine.pool, 'size', 'N/A'),
                    'pool_checked_out': getattr(self.engine.pool, 'checkedout', 'N/A')
                }
                
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否正常
        """
        try:
            if not self.engine:
                return False
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return True
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def migrate_database(self, target_url: str) -> bool:
        """
        迁移数据库到另一个后端
        
        Args:
            target_url: 目标数据库URL
            
        Returns:
            迁移是否成功
        """
        try:
            # 创建目标数据库管理器
            target_manager = DatabaseManager(target_url)
            if not target_manager.connect():
                raise RuntimeError("Failed to connect to target database")
            
            # 创建目标数据库表
            if not target_manager.create_tables():
                raise RuntimeError("Failed to create tables in target database")
            
            logger.info("Starting database migration...")
            
            # 迁移数据的顺序很重要，需要遵循外键依赖
            migration_order = [
                (Company, 'companies'),
                (ReportType, 'report_types'),
                (ReportSection, 'report_sections'),
                (Metric, 'metrics'),
                (FinancialData, 'financial_data'),
                (InvalidMetricCache, 'invalid_metric_cache'),
                (DataFetchLog, 'data_fetch_logs')
            ]
            
            with self.get_session() as source_session, target_manager.get_session() as target_session:
                for model_class, table_name in migration_order:
                    # 获取源数据
                    source_records = source_session.query(model_class).all()
                    
                    if source_records:
                        logger.info(f"Migrating {len(source_records)} records from {table_name}")
                        
                        # 复制到目标数据库
                        for record in source_records:
                            # 创建新记录，排除主键
                            record_dict = {
                                column.name: getattr(record, column.name)
                                for column in record.__table__.columns
                                if column.name != 'id'  # 排除自增主键
                            }
                            
                            new_record = model_class(**record_dict)
                            target_session.add(new_record)
                        
                        target_session.commit()
                    else:
                        logger.info(f"No records to migrate from {table_name}")
            
            logger.info("Database migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 便利函数
def create_database_manager(
    database_type: str = 'sqlite',
    database_config: Optional[Dict[str, Any]] = None
) -> DatabaseManager:
    """
    创建数据库管理器的便利函数
    
    Args:
        database_type: 数据库类型 ('sqlite', 'postgresql', 'mysql')
        database_config: 数据库配置
        
    Returns:
        配置好的数据库管理器
    """
    config = database_config or {}
    config['type'] = database_type
    
    manager = DatabaseManager(config=config)
    
    if not manager.connect():
        raise RuntimeError(f"Failed to connect to {database_type} database")
    
    return manager


def get_default_sqlite_manager() -> DatabaseManager:
    """
    获取默认SQLite数据库管理器
    
    Returns:
        SQLite数据库管理器
    """
    return create_database_manager('sqlite')


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)
    
    # 测试SQLite连接
    print("Testing SQLite connection...")
    manager = get_default_sqlite_manager()
    
    # 创建表
    if manager.create_tables():
        print("✅ Tables created successfully")
    
    # 获取数据库信息
    info = manager.get_database_info()
    print(f"Database info: {info}")
    
    # 关闭连接
    manager.close()
    print("✅ Test completed")