import React from 'react';
import { Shield } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-[#0F172A] border-t border-slate-800/80 mt-auto text-slate-400 text-xs">
      <div className="container mx-auto px-4 lg:px-6 py-6">
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded-lg bg-purple-600/20 text-purple-400 border border-purple-500/30 flex items-center justify-center">
              <Shield size={14} />
            </div>
            <span className="font-semibold text-slate-200">
              CivicPulse • AI Infrastructure Verification & Prioritization System
            </span>
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>YOLOv8 Computer Vision Pipeline</span>
            <span>•</span>
            <span>FastAPI & PostgreSQL Backend</span>
            <span>•</span>
            <span>&copy; {new Date().getFullYear()} CivicPulse</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
