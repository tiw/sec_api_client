import React from 'react';

const TestStyles = () => {
  return (
    <div className="p-4 bg-red-500 text-white">
      <h1 className="text-2xl font-bold">Tailwind Test</h1>
      <div className="mt-4 p-2 bg-blue-500 border-2 border-black">
        <p className="text-sm">如果你能看到红色背景和蓝色框，说明Tailwind正在工作</p>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-2">
        <div className="bg-green-500 p-2">Grid 1</div>
        <div className="bg-yellow-500 p-2">Grid 2</div>
        <div className="bg-purple-500 p-2">Grid 3</div>
      </div>
    </div>
  );
};

export default TestStyles;