import { Brain, Zap, Shield, Code } from "lucide-react";
import { motion } from "framer-motion";

export default function About() {
  return (
    <div className="min-h-[calc(100vh-4rem)] bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 text-white">

      <div className="max-w-6xl mx-auto px-6 py-20">

        {/* Title */}
        <div className="text-center mb-16">

          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold mb-4"
          >
            <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              About EduSphere
            </span>
          </motion.h1>

          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            EduSphere transforms how you interact with documents by combining
            Retrieval-Augmented Generation with powerful AI models to extract
            knowledge instantly.
          </p>

        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-2 gap-8">

          {/* Card */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gradient-to-br from-slate-800/80 to-indigo-900/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-xl hover:shadow-purple-500/20 transition"
          >
            <Brain className="text-purple-400 mb-4" size={32} />

            <h3 className="text-xl font-semibold mb-3">
              Intelligent Processing
            </h3>

            <p className="text-gray-300">
              Our AI analyzes your documents using advanced natural language
              processing to understand context and extract meaningful insights.
            </p>
          </motion.div>

          {/* Card */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gradient-to-br from-slate-800/80 to-indigo-900/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-xl hover:shadow-purple-500/20 transition"
          >
            <Zap className="text-blue-400 mb-4" size={32} />

            <h3 className="text-xl font-semibold mb-3">
              Lightning Fast
            </h3>

            <p className="text-gray-300">
              Optimized retrieval algorithms deliver answers in milliseconds
              using vector search and reranking techniques.
            </p>
          </motion.div>

          {/* Card */}
          <motion.div
            whileHover={{ scale: 1.05 }}
           className="bg-gradient-to-br from-slate-800/80 to-indigo-900/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-xl hover:shadow-purple-500/20 transition" 
          >
            <Shield className="text-green-400 mb-4" size={32} />

            <h3 className="text-xl font-semibold mb-3">
              Secure & Private
            </h3>

            <p className="text-gray-300">
              Your documents are processed securely and never shared. Privacy
              and data protection remain our highest priority.
            </p>
          </motion.div>

          {/* Card */}
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-gradient-to-br from-slate-800/80 to-indigo-900/80 backdrop-blur-md border border-white/10 rounded-2xl p-8 shadow-xl hover:shadow-purple-500/20 transition"
          >
            <Code className="text-pink-400 mb-4" size={32} />

            <h3 className="text-xl font-semibold mb-3">
              Modern AI Stack
            </h3>

            <p className="text-gray-300">
              Built with React, FastAPI, FAISS, and Llama-3 to provide a
              seamless AI-powered document intelligence platform.
            </p>
          </motion.div>

        </div>

        {/* RAG explanation */}
        <div className="mt-20 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-10 text-center">

          <h2 className="text-2xl font-bold mb-4">
            What is RAG?
          </h2>

          <p className="text-blue-100 max-w-3xl mx-auto leading-relaxed">
            Retrieval-Augmented Generation combines large language models with
            your own documents. EduSphere retrieves relevant information from
            PDFs using vector search and feeds it to an AI model to generate
            accurate, context-aware answers.
          </p>

        </div>

      </div>

    </div>
  );
}