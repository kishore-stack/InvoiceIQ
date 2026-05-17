import { Link, useLocation } from 'react-router-dom';
import { FileText, LayoutDashboard, Upload } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-2 rounded-lg">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent">
                InvoiceIQ
              </span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden sm:ml-8 sm:flex sm:space-x-4">
              <Link
                to="/"
                className={`inline-flex items-center px-4 py-2 border-b-2 text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload
              </Link>
              <Link
                to="/dashboard"
                className={`inline-flex items-center px-4 py-2 border-b-2 text-sm font-medium transition-colors ${
                  isActive('/dashboard')
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <LayoutDashboard className="w-4 h-4 mr-2" />
                Dashboard
              </Link>
            </div>
          </div>

          {/* Right side - Status indicator */}
          <div className="flex items-center">
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>System Ready</span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="sm:hidden border-t border-gray-200">
        <div className="flex justify-around py-2">
          <Link
            to="/"
            className={`flex flex-col items-center px-4 py-2 text-xs font-medium ${
              isActive('/')
                ? 'text-blue-600'
                : 'text-gray-500'
            }`}
          >
            <Upload className="w-5 h-5 mb-1" />
            Upload
          </Link>
          <Link
            to="/dashboard"
            className={`flex flex-col items-center px-4 py-2 text-xs font-medium ${
              isActive('/dashboard')
                ? 'text-blue-600'
                : 'text-gray-500'
            }`}
          >
            <LayoutDashboard className="w-5 h-5 mb-1" />
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
