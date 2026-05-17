import { useNavigate, useRouteError } from 'react-router-dom';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

const ErrorPage = () => {
  const navigate = useNavigate();
  const error = useRouteError();

  const getErrorDetails = () => {
    if (error?.status === 404) {
      return {
        title: 'Page Not Found',
        message: 'The page you are looking for does not exist.',
        icon: '🔍',
      };
    } else if (error?.status === 500) {
      return {
        title: 'Server Error',
        message: 'An internal server error occurred. Please try again later.',
        icon: '⚠️',
      };
    } else if (error?.message?.includes('OCR')) {
      return {
        title: 'OCR Processing Failed',
        message: 'Unable to extract text from the uploaded document. Please ensure the image is clear and readable.',
        icon: '📄',
      };
    } else if (error?.message?.includes('network') || error?.message?.includes('fetch')) {
      return {
        title: 'Network Error',
        message: 'Unable to connect to the server. Please check your internet connection and ensure the backend is running.',
        icon: '🌐',
      };
    } else if (error?.message?.includes('file') || error?.message?.includes('upload')) {
      return {
        title: 'Invalid File',
        message: 'The uploaded file is invalid or corrupted. Please upload a valid image or PDF file.',
        icon: '📁',
      };
    }

    return {
      title: 'Something Went Wrong',
      message: error?.message || error?.statusText || 'An unexpected error occurred.',
      icon: '❌',
    };
  };

  const errorDetails = getErrorDetails();

  const handleGoHome = () => {
    navigate('/');
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12 border border-red-100">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-24 h-24 bg-red-100 rounded-full flex items-center justify-center">
              <span className="text-5xl">{errorDetails.icon}</span>
            </div>
          </div>

          {/* Error Details */}
          <div className="text-center mb-8">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              {errorDetails.title}
            </h1>
            <p className="text-lg text-gray-600 mb-2">
              {errorDetails.message}
            </p>
            
            {/* Technical Details */}
            {(error?.status || error?.statusText) && (
              <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-sm font-mono text-gray-700">
                  {error.status && <span>Error {error.status}</span>}
                  {error.status && error.statusText && <span> - </span>}
                  {error.statusText && <span>{error.statusText}</span>}
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={handleGoHome}
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
            >
              <Home className="w-5 h-5" />
              <span>Go to Home</span>
            </button>
            
            <button
              onClick={handleRefresh}
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-white hover:bg-gray-50 text-gray-700 font-semibold rounded-lg border border-gray-300 transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
              <span>Refresh Page</span>
            </button>
          </div>

          {/* Help Text */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-1">Common Solutions:</p>
                <ul className="list-disc list-inside space-y-1 text-blue-700">
                  <li>Ensure the backend server is running at the correct URL</li>
                  <li>Check that your file is a valid image (JPG, PNG) or PDF</li>
                  <li>Verify your internet connection is stable</li>
                  <li>Try uploading a different file with clearer text</li>
                  <li>Contact support if the issue persists</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ErrorPage;
