import { FileText, Brain, Database, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

const features = [
  {
    icon: FileText,
    title: "Upload Documents",
    desc: "Upload PDFs and let AI process the content instantly."
  },
  {
    icon: Brain,
    title: "AI Embeddings",
    desc: "Advanced embedding models convert documents into semantic vectors."
  },
  {
    icon: Database,
    title: "Vector Retrieval",
    desc: "FAISS vector database retrieves the most relevant information."
  },
  {
    icon: Sparkles,
    title: "AI Answers",
    desc: "Groq Llama-3 generates accurate answers using retrieved context."
  }
];

export default function FeatureCards() {
  return (
    <div className="py-20 bg-gray-50">

      <h2 className="text-center text-3xl font-bold mb-12">
        How EduSphere Works
      </h2>

      <div className="grid md:grid-cols-4 gap-8 max-w-6xl mx-auto">

        {features.map((feature, i) => (
          <motion.div
            key={i}
            whileHover={{ scale: 1.05 }}
            className="bg-white rounded-xl shadow p-6 text-center"
          >
            <feature.icon className="mx-auto mb-4 text-blue-600" size={32} />
            <h3 className="font-semibold mb-2">{feature.title}</h3>
            <p className="text-sm text-gray-500">{feature.desc}</p>
          </motion.div>
        ))}

      </div>

    </div>
  );
}