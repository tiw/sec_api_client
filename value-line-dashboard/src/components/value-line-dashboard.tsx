import React from 'react';

const ValueLineDashboard = () => {
  return (
    <div className="min-h-screen bg-white p-1 font-mono">
      <div className="max-w-[1400px] mx-auto">
        
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
                <div className="text-[10px]">
                  {/* 评级表格 - 确保列对齐 */}
                  <table className="w-full mb-2">
                    <colgroup>
                      <col className="w-auto" />
                      <col className="w-4" />
                      <col className="w-auto" />
                    </colgroup>
                    <tbody>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">TIMELINESS</td>
                        <td className="text-center py-0.25 w-4">
                          <div className="w-4 h-4 bg-black text-white rounded-full flex items-center justify-center font-bold text-[8px] mx-auto">2</div>
                        </td>
                        <td className="text-gray-600 text-right py-0.25 text-[10px] font-sans whitespace-nowrap">Raised 2/28/25</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">SAFETY</td>
                        <td className="text-center py-0.25 w-4">
                          <div className="w-4 h-4 bg-black text-white rounded-full flex items-center justify-center font-bold text-[8px] mx-auto">1</div>
                        </td>
                        <td className="text-gray-600 text-right py-0.25 text-[10px] font-sans whitespace-nowrap">Raised 4/17/20</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">TECHNICAL</td>
                        <td className="text-center py-0.25 w-4">
                          <div className="w-4 h-4 bg-black text-white rounded-full flex items-center justify-center font-bold text-[8px] mx-auto">3</div>
                        </td>
                        <td className="text-gray-600 text-right py-0.25 text-[10px] font-sans whitespace-nowrap">Lowered 2/28/25</td>
                      </tr>
                    </tbody>
                  </table>
                  
                  {/* Beta 行 */}
                  <div className="flex items-center justify-between border-t border-gray-300 pt-1">
                    <span className="font-semibold text-[10px] font-sans">BETA</span>
                    <span className="font-bold text-[10px]">.90</span>
                    <span className="text-gray-600 text-[10px] font-sans">(1.00 = Market)</span>
                  </div>
                </div>
              </div>

              {/* 目标价格区间 */}
              <div className="border-b border-black p-1">
                <div className="text-[10px]">
                  <table className="w-full">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-0.5 text-[10px] font-sans" colSpan={2}>18-Month Target Price Range</td>
                      </tr>
                      <tr>
                        <td className="py-0.5 text-[10px] font-sans">Low-High</td>
                        <td className="text-right py-0.5 text-[10px] font-sans">Midpoint (% to Mid.)</td>
                      </tr>
                      <tr>
                        <td className="font-bold py-0.5 text-[10px] font-sans">$195-$375</td>
                        <td className="text-right font-bold py-0.5 text-[10px] font-sans">$285 (25%)</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 2028-30预测 */}
              <div className="border-b border-black p-0.5">
                <div className="text-[10px]">
                  <table className="w-full">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-0.5 text-[10px] font-sans" colSpan={4}>2028-30 PROJECTIONS</td>
                      </tr>
                      <tr>
                        <td className="py-0.25 text-[10px] font-sans align-bottom"></td>
                        <td className="font-semibold text-center py-0.25 text-[10px] font-sans align-bottom">Price</td>
                        <td className="font-semibold text-center py-0.25 text-[10px] font-sans align-bottom">Gain</td>
                        <td className="font-semibold text-center py-0.25 text-[10px] font-sans align-bottom">Ann'l Total Return</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">High</td>
                        <td className="font-bold text-center py-0.25 text-[10px] font-sans">390</td>
                        <td className="font-bold text-center py-0.25 text-[10px] font-sans">(+70%)</td>
                        <td className="font-bold text-center py-0.25 text-[10px] font-sans">15%</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">Low</td>
                        <td className="font-bold text-center py-0.25 text-[10px] font-sans">320</td>
                        <td className="font-bold text-center py-0.25 text-[10px] font-sans">(+40%)</td>
                        <td className="font-bold text-center py-0.25 text-[10px] font-sans">10%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* 机构决策 */}
              <div className="p-0.5 flex-1">
                <div className="text-[10px]">
                  <table className="w-full">
                    <tbody>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans" colSpan={3}>Institutional Decisions</td>
                      </tr>
                      <tr>
                        <td className="py-0.25 text-[10px] font-sans"></td>
                        <td className="font-semibold text-center py-0.25 text-[10px] font-sans">2Q2024</td>
                        <td className="font-semibold text-center py-0.25 text-[10px] font-sans">3Q2024</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">to Buy</td>
                        <td className="text-center py-0.25 text-[10px] font-sans">2409</td>
                        <td className="text-center py-0.25 text-[10px] font-sans">2115</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">to Sell</td>
                        <td className="text-center py-0.25 text-[10px] font-sans">2372</td>
                        <td className="text-center py-0.25 text-[10px] font-sans">2682</td>
                      </tr>
                      <tr>
                        <td className="font-semibold py-0.25 text-[10px] font-sans">Hld's(000)</td>
                        <td className="text-center py-0.25 text-[10px] font-sans">9286688</td>
                        <td className="text-center py-0.25 text-[10px] font-sans">2923361</td>
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
                
                {/* 图表网格 */}
                <div className="absolute inset-2 grid grid-cols-18 grid-rows-10 opacity-30">
                  {Array.from({ length: 180 }).map((_, i) => (
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
                  <span>2010</span>
                  <span>2011</span>
                  <span>2012</span>
                  <span>2013</span>
                  <span>2014</span>
                  <span>2015</span>
                  <span>2016</span>
                  <span>2017</span>
                  <span>2018</span>
                  <span>2019</span>
                  <span>2020</span>
                  <span>2021</span>
                  <span>2022</span>
                  <span>2023</span>
                  <span>2024</span>
                  <span>2025</span>
                  <span>2026</span>
                </div>
                
                {/* 股价走势线 */}
                <div className="absolute inset-4">
                  <svg className="w-full h-full">
                    <path
                      d="M 0 90 L 30 88 L 60 85 L 90 82 L 120 78 L 150 75 L 180 70 L 210 65 L 240 60 L 270 50 L 300 45 L 330 40 L 360 35 L 390 30 L 420 25 L 450 30 L 480 35 L 510 40"
                      stroke="black"
                      strokeWidth="1.5"
                      fill="none"
                    />
                    <path
                      d="M 0 95 L 30 92 L 60 90 L 90 87 L 120 83 L 150 80 L 180 75 L 210 70 L 240 65 L 270 55 L 300 50 L 330 45 L 360 40 L 390 35 L 420 30 L 450 35 L 480 40 L 510 45"
                      stroke="gray"
                      strokeWidth="1"
                      strokeDasharray="2,2"
                      fill="none"
                    />
                  </svg>
                </div>
                
                {/* 成交量柱状图 */}
                <div className="absolute bottom-8 left-8 right-8 h-6 flex items-end justify-between">
                  {Array.from({ length: 18 }).map((_, i) => (
                    <div key={i} className="bg-black w-1" style={{height: `${Math.random() * 100}%`}}></div>
                  ))}
                </div>

                {/* 图例信息 */}
                <div className="absolute top-2 left-2 text-xs">
                  <div>High: 29.9 33.6 29.7 44.3 58.4 73.5 138.8 182.1 182.9 199.6 260.1 250.0</div>
                  <div>Low: 17.6 23.0 22.4 28.7 36.6 35.5 53.2 116.2 125.9 124.2 164.1 219.4</div>
                </div>
                
              <div className="absolute top-12 left-2 text-xs bg-white border border-black p-2">
                <div>LEGENDS</div>
                <div>28.0 x "Cash Flow" p sh</div>
                <div>Relative Price Strength</div>
                <div>7-for-1 split 6/14</div>
                <div>4-for-1 split 8/20</div>
                <div>Options: Yes</div>
                <div>Shaded area indicates recession</div>
              </div>

                {/* % TOT RETURN 浮层 - 位于图表右上角 */}
              <div className="absolute bottom-2 right-2 bg-white border border-black p-1 text-xs">
                <div className="font-semibold mb-0.5">% TOT RETURN 2/25</div>
                <table className="text-xs">
                  <colgroup>
                    <col className="w-8" />
                    <col className="w-10" />
                    <col className="w-14" />
                  </colgroup>
                  <thead>
                    <tr>
                      <th></th>
                      <th className="font-semibold text-center px-0.5">THIS STOCK</th>
                      <th className="font-semibold text-center px-0.5">VL ARITH INDEX</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="text-left py-0 pr-0 text-[10px]">1 Yr.</td>
                      <td className="font-bold text-center py-0">35.4</td>
                      <td className="text-center py-0">12.1</td>
                    </tr>
                    <tr>
                      <td className="text-left py-0 pr-0 text-[10px]">3 Yr.</td>
                      <td className="font-bold text-center py-0">49.9</td>
                      <td className="text-center py-0">20.8</td>
                    </tr>
                    <tr>
                      <td className="text-left py-0 pr-0 text-[10px]">5 Yr.</td>
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
            <div className="flex-1 overflow-x-auto -ml-52">
              <table className="w-full border-collapse">
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
                    <td className="text-right p-1 border-r border-black text-[10px]">8.24</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">9.87</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">10.15</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">9.96</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">10.35</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">10.42</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">10.47</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">10.10</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">11.18</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">13.96</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">14.64</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">16.17</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">21.55</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">24.73</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">24.65</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">25.87</td>
                    <td className="text-right p-1 border-r border-black text-[10px] font-bold">27.75</td>
                    <td className="text-right p-1 text-[10px] font-bold">32.00</td>
                  </tr>
                  <tr className="border-b border-gray-300">
                    <td className="text-right p-1 border-r border-black text-[10px]">2.15</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.45</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.68</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.72</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.85</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.88</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.90</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.63</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.85</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.70</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.82</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">4.03</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.24</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.96</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.98</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.96</td>
                    <td className="text-right p-1 border-r border-black text-[10px] font-bold">8.25</td>
                    <td className="text-right p-1 text-[10px] font-bold">9.40</td>
                  </tr>
                  <tr className="border-b border-gray-300">
                    <td className="text-right p-1 border-r border-black text-[10px]">1.89</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.16</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.40</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.20</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.28</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.18</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.31</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.08</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.30</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.98</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">2.97</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.28</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.61</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.11</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.13</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.08</td>
                    <td className="text-right p-1 border-r border-black text-[10px] font-bold">7.30</td>
                    <td className="text-right p-1 text-[10px] font-bold">8.20</td>
                  </tr>
                  <tr className="border-b border-gray-300">
                    <td className="text-right p-1 border-r border-black text-[10px]">.00</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.00</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.00</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.38</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.43</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.47</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.50</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.55</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.60</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.68</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.75</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.80</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.85</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.90</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.94</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.99</td>
                    <td className="text-right p-1 border-r border-black text-[10px] font-bold">1.10</td>
                    <td className="text-right p-1 text-[10px] font-bold">1.20</td>
                  </tr>
                  <tr className="border-b border-gray-300">
                    <td className="text-right p-1 border-r border-black text-[10px]">.35</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.42</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.45</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.48</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.52</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.49</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.50</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.60</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.61</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.70</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.59</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.43</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.65</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.67</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.70</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">.62</td>
                    <td className="text-right p-1 border-r border-black text-[10px] font-bold">.80</td>
                    <td className="text-right p-1 text-[10px] font-bold">.85</td>
                  </tr>
                  <tr>
                    <td className="text-right p-1 border-r border-black text-[10px]">4.85</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.12</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.45</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.28</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.18</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.25</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.35</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.01</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">6.54</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.63</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">5.09</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.85</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.72</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.18</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">4.00</td>
                    <td className="text-right p-1 border-r border-black text-[10px]">3.77</td>
                    <td className="text-right p-1 border-r border-black text-[10px] font-bold">4.55</td>
                    <td className="text-right p-1 text-[10px] font-bold">5.00</td>
                  </tr>
                </tbody>
              </table>
            </div>

                {/* 右侧独立的两列表格 */}
                <div className="w-48 border-l-2 border-black">
                  <table className="w-full text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-black">
                        <th className="text-center p-1 font-bold" colSpan={2}>© VALUE LINE PUB. LLC 28-30</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Sales per sh A</td>
                        <td className="text-center p-1 font-bold">40.80</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">"Cash Flow" per sh</td>
                        <td className="text-center p-1 font-bold">12.70</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Earnings per sh B</td>
                        <td className="text-center p-1 font-bold">11.50</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Div'ds Decl'd per sh E</td>
                        <td className="text-center p-1 font-bold">1.50</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Cap'l Spending per sh</td>
                        <td className="text-center p-1 font-bold">1.00</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Book Value per sh</td>
                        <td className="text-center p-1 font-bold">6.00</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Common Shs Outst'g C</td>
                        <td className="text-center p-1 font-bold">12500</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Avg Ann'l P/E Ratio</td>
                        <td className="text-center p-1 font-bold">31.0</td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1 border-r border-black font-semibold">Relative P/E Ratio</td>
                        <td className="text-center p-1 font-bold">1.70</td>
                      </tr>
                      <tr>
                        <td className="p-1 border-r border-black font-semibold">Avg Ann'l Div'd Yield</td>
                        <td className="text-center p-1 font-bold">.4%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          {/* 底部业务描述 */}
          <div className="border-t-2 border-black p-2 text-xs">
            <strong>BUSINESS:</strong> Apple Inc., established in 1977, is one of the world's largest technology companies. 
            Pay, and a host of digital content from the popular iTunes store and App Store.
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValueLineDashboard;