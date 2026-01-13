import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ProjectPage from './pages/ProjectPage';
import AiAssistant from './components/AiAssistant';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/project/:projectKey" element={<ProjectPage />} />
      </Routes>
      {/* AI小助手 - 全局显示在所有页面 */}
      <AiAssistant />
    </BrowserRouter>
  );
}

export default App;
