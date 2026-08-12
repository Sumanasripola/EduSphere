import { ArrowRight, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import AnimatedBackground from "./AnimatedBackground";
import DocumentAnimation from "./DocumentAnimation";

export default function Hero({ onGetStarted }) {
  return (
    <div className="relative min-h-screen flex items-center overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900">

      {/* Animated particle background */}
      <AnimatedBackground />

      <div className="relative z-10 max-w-7xl mx-auto px-6 grid md:grid-cols-2 gap-12 items-center">

        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >

          <div className="flex items-center gap-2 mb-4 text-purple-400">
            <Sparkles size={20} />
            <span className="text-sm tracking-wider">
              AI Powered Document Intelligence
            </span>
          </div>

          <h1 className="text-6xl font-bold mb-6 leading-tight">
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              EduSphere
            </span>
          </h1>

          <p className="text-xl text-gray-300 mb-10 max-w-lg">
            Upload PDFs, ask questions, and extract knowledge instantly using
            Retrieval-Augmented Generation and AI.
          </p>

          <button
            onClick={onGetStarted}
            className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-xl shadow-lg hover:scale-105 transition"
          >
            Start Exploring
            <ArrowRight size={18} />
          </button>

        </motion.div>

        {/* Right Animation */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          className="flex justify-center"
        >
          <DocumentAnimation />
        </motion.div>

      </div>

    </div>
  );
}