import { Github } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        <div className="flex flex-col items-center space-y-4">

          <div className="flex items-center space-x-2">
            <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              EduSphere
            </span>
          </div>

          <p className="text-sm text-gray-600 text-center">
            Your Personalized Gateway to Document Intelligence
          </p>

          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-600 hover:text-gray-900 transition-colors"
          >
            
          </a>

          <p className="text-xs text-gray-500">
            © 2026 EduSphere. All rights reserved.
          </p>

        </div>

      </div>

    </footer>
  );
}