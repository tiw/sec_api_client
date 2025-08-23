import React from 'react';

const ValueLineDashboard = () => {
  return (
    <div className="min-h-screen bg-white p-1 font-mono">
      <div className="max-w-7xl mx-auto">
        
        {/* 完整的Value Line报告布局 */}
        <div className="border-2 border-black">
          
          {/* 顶部标题栏 */}
          <div className="border-b-2 border-black p-1 flex justify-between items-center bg-white">
            <div className="flex items-center space-x-4 text-sm">
              <span className="text-xl font-bold">APPLE INC. NDQ-AAPL</span>
              <span className="font-semibold">RECENT PRICE</span>
              <span className="text-2xl font-bold">227.48</span>
              <span className="font-semibold">P/E RATIO</span>
              <span className="font-bold">31.2</span>
              <span className="text-xs">(Trailing: 36.1, Median: 20.0)</span>
              <span className="font-semibold">RELATIVE P/E RATIO</span>
              <span className="font-bold">1.78</span>
              <span className="font-semibold">DIV'D YLD</span>
              <span className="font-bold">0.4%</span>
            </div>
            <div className="bg-black text-white px-3 py-1">
              <span className="font-bold">VALUE LINE</span>
            </div>
          </div>

          {/* 主要内容区域 */}
          <div className="flex">
            
            {/* 左侧列 - 评级和信息 */}
            <div className="w-52 border-2 border-black h-80">
              
              {/* 评级区域 */}
              <div className="border-b border-black p-1">
                <div className="text-xs">
                  {/* 评级表格 */}
                  <table className="w-full mb-2">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">TIMELINESS</td>
                        <td className="text-center py-1 w-4">
                          <div className="w-4 h-4 bg-black text-white rounded-full flex items-center justify-center font-bold text-xs mx-auto">2</div>
                        </td>
                        <td className="text-gray-600 text-right py-1 text-xs font-sans whitespace-nowrap">Raised 2/28/25</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">SAFETY</td>
                        <td className="text-center py-1 w-4">
                          <div className="w-4 h-4 bg-black text-white rounded-full flex items-center justify-center font-bold text-xs mx-auto">1</div>
                        </td>
                        <td className="text-gray-600 text-right py-1 text-xs font-sans whitespace-nowrap">Raised 4/17/20</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">TECHNICAL</td>
                        <td className="text-center py-1 w-4">
                          <div className="w-4 h-4 bg-black text-white rounded-full flex items-center justify-center font-bold text-xs mx-auto">3</div>
                        </td>
                        <td className="text-gray-600 text-right py-1 text-xs font-sans whitespace-nowrap">Lowered 2/28/25</td>
                      </tr>
                    </tbody>
                  </table>
                  
                  {/* Beta 行 */}
                  <div className="flex items-center justify-between border-t border-gray-300 pt-1">
                    <span className="font-semibold text-xs font-sans">BETA</span>
                    <span className="font-bold text-xs">.90</span>
                    <span className="text-gray-600 text-xs font-sans">(1.00 = Market)</span>
                  </div>
                </div>
              </div>

              {/* 目标价格区间 */}
              <div className="border-b border-black p-1">
                <div className="text-xs">
                  <table className="w-full">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans" colSpan={2}>18-Month Target Price Range</td>
                      </tr>
                      <tr>
                        <td className="py-1 text-xs font-sans">Low-High</td>
                        <td className="text-right py-1 text-xs font-sans">Midpoint (% to Mid.)</td>
                      </tr>
                      <tr>
                        <td className="font-bold py-1 text-xs font-sans">$195-$375</td>
                        <td className="text-right font-bold py-1 text-xs font-sans">$285 (25%)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 2028-30预测 */}
              <div className="border-b border-black p-1">
                <div className="text-xs">
                  <table className="w-full">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans" colSpan={4}>2028-30 PROJECTIONS</td>
                      </tr>
                      <tr>
                        <td className="py-1 text-xs font-sans"></td>
                        <td className="font-semibold text-center py-1 text-xs font-sans">Price</td>
                        <td className="font-semibold text-center py-1 text-xs font-sans">Gain</td>
                        <td className="font-semibold text-center py-1 text-xs font-sans">Ann'l Total Return</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">High</td>
                        <td className="font-bold text-center py-1 text-xs font-sans">390</td>
                        <td className="font-bold text-center py-1 text-xs font-sans">(+70%)</td>
                        <td className="font-bold text-center py-1 text-xs font-sans">15%</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">Low</td>
                        <td className="font-bold text-center py-1 text-xs font-sans">320</td>
                        <td className="font-bold text-center py-1 text-xs font-sans">(+40%)</td>
                        <td className="font-bold text-center py-1 text-xs font-sans">10%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 机构决策 */}
              <div className="p-1 flex-1">
                <div className="text-xs">
                  <table className="w-full">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans" colSpan={3}>Institutional Decisions</td>
                      </tr>
                      <tr>
                        <td className="py-1 text-xs font-sans"></td>
                        <td className="font-semibold text-center py-1 text-xs font-sans">2Q2024</td>
                        <td className="font-semibold text-center py-1 text-xs font-sans">3Q2024</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">to Buy</td>
                        <td className="text-center py-1 text-xs font-sans">2409</td>
                        <td className="text-center py-1 text-xs font-sans">2115</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">to Sell</td>
                        <td className="text-center py-1 text-xs font-sans">2372</td>
                        <td className="text-center py-1 text-xs font-sans">2682</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-1 text-xs font-sans">Hld's(000)</td>
                        <td className="text-center py-1 text-xs font-sans">9286688</td>
                        <td className="text-center py-1 text-xs font-sans">2923361</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* 中央区域 - 图表和数据表 */}
            <div className="flex-1">
              
              {/* 股价图表区域 */}
              <div className="h-80 border-b border-black relative bg-white">
                
                {/* 图表网格 - 使用标准grid类 */}
                <div className="absolute inset-2 grid grid-cols-12 grid-rows-8 opacity-30">
                  {Array.from({ length: 96 }).map((_, i) => (
                    <div key={i} className="border border-gray-400"></div>
                  ))}
                </div>
                
                {/* 价格刻度 */}
                <div className="absolute right-2 top-2 h-full flex flex-col justify-between text-xs">
                  <span>800</span>
                  <span>600</span>
                  <span>500</span>
                  <span>400</span>
                  <span>300</span>
                  <span>250</span>
                  <span>200</span>
                  <span>150</span>
                  <span>100</span>
                  <span>75</span>
                </div>
                
                {/* 年份标签 */}
                <div className="absolute bottom-2 left-8 right-8 flex justify-between text-xs">
                  <span>2009</span>
                  <span>2011</span>
                  <span>2013</span>
                  <span>2015</span>
                  <span>2017</span>
                  <span>2019</span>
                  <span>2021</span>
                  <span>2023</span>
                  <span>2025</span>
                </div>
                
                {/* 股价走势线 */}
                <div className="absolute inset-4">
                  <svg className="w-full h-full">
                    <path
                      d="M 0 90 L 50 85 L 100 80 L 150 75 L 200 70 L 250 60 L 300 50 L 350 40 L 400 35 L 450 30"
                      stroke="black"
                      strokeWidth="2"
                      fill="none"
                    />
                    <path
                      d="M 0 95 L 50 90 L 100 85 L 150 80 L 200 75 L 250 65 L 300 55 L 350 45 L 400 40 L 450 35"
                      stroke="gray"
                      strokeWidth="1"
                      strokeDasharray="3,3"
                      fill="none"
                    />
                  </svg>
                </div>
                
                {/* 成交量柱状图 */}
                <div className="absolute bottom-8 left-8 right-8 h-6 flex items-end justify-between">
                  {Array.from({ length: 12 }).map((_, i) => (
                    <div key={i} className="bg-black w-2" style={{height: `${Math.random() * 100}%`}}></div>
                  ))}
                </div>

                {/* 图例信息 */}
                <div className="absolute top-2 left-2 text-xs">
                  <div>High: 29.9 33.6 29.7 44.3 58.4 73.5 138.8 182.1 182.9 199.6 260.1 250.0</div>
                  <div>Low: 17.6 23.0 22.4 28.7 36.6 35.5 53.2 116.2 125.9 124.2 164.1 219.4</div>
                </div>
                
                {/* LEGENDS 浮层 */}
                <div className="absolute top-12 left-2 text-xs bg-white border border-black p-2">
                  <div className="font-bold">LEGENDS</div>
                  <div>28.0 x "Cash Flow" p sh</div>
                  <div>Relative Price Strength</div>
                  <div>7-for-1 split 6/14</div>
                  <div>4-for-1 split 8/20</div>
                  <div>Options: Yes</div>
                  <div>Shaded area indicates recession</div>
                </div>

                {/* % TOT RETURN 浮层 */}
                <div className="absolute bottom-2 right-2 bg-white border border-black p-1 text-xs">
                  <div className="font-semibold mb-1">% TOT RETURN 2/25</div>
                  <table className="text-xs">
                    <thead>
                      <tr>
                        <th></th>
                        <th className="font-semibold text-center px-1">THIS STOCK</th>
                        <th className="font-semibold text-center px-1">VL ARITH INDEX</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="text-left py-0 pr-1 text-xs">1 Yr.</td>
                        <td className="font-bold text-center py-0">35.4</td>
                        <td className="text-center py-0">12.1</td>
                      </tr>
                      <tr>
                        <td className="text-left py-0 pr-1 text-xs">3 Yr.</td>
                        <td className="font-bold text-center py-0">49.9</td>
                        <td className="text-center py-0">20.8</td>
                      </tr>
                      <tr>
                        <td className="text-left py-0 pr-1 text-xs">5 Yr.</td>
                        <td className="font-bold text-center py-0">267.1</td>
                        <td className="text-center py-0">96.2</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 财务数据表格区域 */}
              <div className="flex">
                {/* 主要财务数据表格 */}
                <div className="flex-1 overflow-x-auto">
                  <table className="w-full border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-black">
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2009</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2010</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2011</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2012</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2013</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2014</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2015</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2016</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2017</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2018</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2019</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2020</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2021</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2022</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2023</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2024</th>
                        <th className="text-center p-1 border-r border-black text-sm font-bold">2025</th>
                        <th className="text-center p-1 text-sm font-bold">2026</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-300">
                        <td className="text-right p-1 border-r border-black text-xs">8.24</td>
                        <td className="text-right p-1 border-r border-black text-xs">9.87</td>
                        <td className="text-right p-1 border-r border-black text-xs">10.15</td>
                        <td className="text-right p-1 border-r border-black text-xs">9.96</td>
                        <td className="text-right p-1 border-r border-black text-xs">10.35</td>
                        <td className="text-right p-1 border-r border-black text-xs">10.42</td>
                        <td className="text-right p-1 border-r border-black text-xs">10.47</td>
                        <td className="text-right p-1 border-r border-black text-xs">10.10</td>
                        <td className="text-right p-1 border-r border-black text-xs">11.18</td>
                        <td className="text-right p-1 border-r border-black text-xs">13.96</td>
                        <td className="text-right p-1 border-r border-black text-xs">14.64</td>
                        <td className="text-right p-1 border-r border-black text-xs">16.17</td>
                        <td className="text-right p-1 border-r border-black text-xs">21.55</td>
                        <td className="text-right p-1 border-r border-black text-xs">24.73</td>
                        <td className="text-right p-1 border-r border-black text-xs">24.65</td>
                        <td className="text-right p-1 border-r border-black text-xs">25.87</td>
                        <td className="text-right p-1 border-r border-black text-xs font-bold">27.75</td>
                        <td className="text-right p-1 text-xs font-bold">32.00</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="text-right p-1 border-r border-black text-xs">2.15</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.45</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.68</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.72</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.85</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.88</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.90</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.63</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.85</td>
                        <td className="text-right p-1 border-r border-black text-xs">3.70</td>
                        <td className="text-right p-1 border-r border-black text-xs">3.82</td>
                        <td className="text-right p-1 border-r border-black text-xs">4.03</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.24</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.96</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.98</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.96</td>
                        <td className="text-right p-1 border-r border-black text-xs font-bold">8.25</td>
                        <td className="text-right p-1 text-xs font-bold">9.40</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="text-right p-1 border-r border-black text-xs">1.89</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.16</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.40</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.20</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.28</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.18</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.31</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.08</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.30</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.98</td>
                        <td className="text-right p-1 border-r border-black text-xs">2.97</td>
                        <td className="text-right p-1 border-r border-black text-xs">3.28</td>
                        <td className="text-right p-1 border-r border-black text-xs">5.61</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.11</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.13</td>
                        <td className="text-right p-1 border-r border-black text-xs">6.08</td>
                        <td className="text-right p-1 border-r border-black text-xs font-bold">7.30</td>
                        <td className="text-right p-1 text-xs font-bold">8.20</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="text-right p-1 border-r border-black text-xs">.00</td>
                        <td className="text-right p-1 border-r border-black text-xs">.00</td>
                        <td className="text-right p-1 border-r border-black text-xs">.00</td>
                        <td className="text-right p-1 border-r border-black text-xs">.38</td>
                        <td className="text-right p-1 border-r border-black text-xs">.43</td>
                        <td className="text-right p-1 border-r border-black text-xs">.47</td>
                        <td className="text-right p-1 border-r border-black text-xs">.50</td>
                        <td className="text-right p-1 border-r border-black text-xs">.55</td>
                        <td className="text-right p-1 border-r border-black text-xs">.60</td>
                        <td className="text-right p-1 border-r border-black text-xs">.68</td>
                        <td className="text-right p-1 border-r border-black text-xs">.75</td>
                        <td className="text-right p-1 border-r border-black text-xs">.80</td>
                        <td className="text-right p-1 border-r border-black text-xs">.85</td>
                        <td className="text-right p-1 border-r border-black text-xs">.90</td>
                        <td className="text-right p-1 border-r border-black text-xs">.94</td>
                        <td className="text-right p-1 border-r border-black text-xs">.99</td>
                        <td className="text-right p-1 border-r border-black text-xs font-bold">1.10</td>
                        <td className="text-right p-1 text-xs font-bold">1.20</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="text-right p-1 border-r border-black text-xs">.35</td>
                        <td className="text-right p-1 border-r border-black text-xs">.42</td>
                        <td className="text-right p-1 border-r border-black text-xs">.45</td>
                        <td className="text-right p-1 border-r border-black text-xs">.48</td>
                        <td className="text-right p-1 border-r border-black text-xs">.52</td>
                        <td className="text-right p-1 border-r border-black text-xs">.49</td>
                        <td className="text-right p-1 border-r border-black text-xs">.50</td>
                        <td className="text-right p-1 border-r border-black text-xs">.60</td>
                        <td className="text-right p-1 border-r border-black text-xs">.61</td>
                        <td className="text-right p-1 border-r border-black text-xs">.70</td>
                        <td className="text-right p-1 border-r border-black text-xs">.59</td>
                        <td className="text-right p-1 border-r border-black text-xs">.43</td>
                        <td className="text-right p-1 border-r border-black text-xs">.65</td>
                        <td className="text-right p-1 border-r border-black text-xs">.67</td>
                        <td className="text-right p-1 border-r border-black text-xs">.73</td>
                        <td className="text-right p-1 border-r border-black text-xs">.85</td>
                        <td className="text-right p-1 border-r border-black text-xs font-bold">.90</td>
                        <td className="text-right p-1 text-xs font-bold">.95</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* 右侧补充信息区域 */}
                <div className="w-48 border-l border-black p-1">
                  <div className="text-xs space-y-2">
                    <div>
                      <div className="font-semibold mb-1">BUSINESS</div>
                      <div className="text-justify leading-tight">
                        Apple Inc. designs, manufactures and markets smartphones, personal computers, tablets, wearables and accessories, and sells a variety of related services.
                      </div>
                    </div>
                    
                    <div>
                      <div className="font-semibold mb-1">RECENT DEVELOPMENTS</div>
                      <div className="text-justify leading-tight">
                        Apple reported Q1 2025 results with revenue of $124.3B (+3.8% YoY) and EPS of $2.18 (+7.4% YoY). iPhone revenue grew 3.5% to $69.1B.
                      </div>
                    </div>

                    <div>
                      <div className="font-semibold mb-1">ANALYST'S COMMENTARY</div>
                      <div className="text-justify leading-tight">
                        Apple continues to benefit from strong iPhone demand and growing services revenue. The company's focus on AI integration positions it well for future growth.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValueLineDashboard;