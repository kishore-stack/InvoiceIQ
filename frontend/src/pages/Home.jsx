import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadBox from '../components/UploadBox';
import api from '../services/api';
import { CheckCircle, AlertCircle, Sparkles, Zap, Shield, Clock } from 'lucide-react';

const Home = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success' | 'error' | null
  const [uploadResult, setUploadResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleUpload = async (files) => {
    setIsLoading(true);
    setUploadProgress(0);
    setUploadStatus(null);
    setErrorMessage('');
    setUploadResult(null);

    try {
      const response = await api.uploadInvoice(files, (progress) => {
        setUploadProgress(progress);
      });

     setUploadStatus('success');
setUploadResult(response.data);

localStorage.setItem("latestInvoiceResult", JSON.stringify(response.data));

setTimeout(() => {
  navigate('/dashboard');
}, 2000);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus('error');
      
      if (error.response) {
        setErrorMessage(error.response.data.message || error.response.data.detail || 'Server error occurred');
      } else if (error.request) {
        setErrorMessage('No response from server. Please check if the backend is running.');
      } else {
        setErrorMessage(error.message || 'An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const features = [
    {
      icon: Sparkles,
      title: 'AI-Powered OCR',
      description: 'Advanced machine learning for accurate text extraction from any invoice format',
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Process multiple invoices in seconds with our optimized pipeline',
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: Shield,
      title: 'Smart Validation',
      description: 'Automatic validation of totals, taxes, and line items for accuracy',
      color: 'from-green-500 to-emerald-500',
    },
    {
      icon: Clock,
      title: 'Save Time',
      description: 'Eliminate manual data entry and reduce processing time by 90%',
      color: 'from-orange-500 to-red-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Extract Invoice Data with
            <span className="bg-gradient-to-r from-blue-600 to-indigo-700 bg-clip-text text-transparent"> AI Precision</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload your invoices and let our advanced OCR technology extract all the data automatically.
            Fast, accurate, and intelligent.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100"
              >
                <div className={`w-12 h-12 bg-gradient-to-br ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-gray-600">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>

        {/* Upload Section */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
            <UploadBox onUpload={handleUpload} isLoading={isLoading} />

            {/* Progress Bar */}
            {isLoading && uploadProgress > 0 && (
              <div className="mt-6">
                <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                  <span>Processing your invoices...</span>
                  <span className="font-semibold">{uploadProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="h-3 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  This may take a few moments depending on file size...
                </p>
              </div>
            )}

            {/* Success Message */}
            {uploadStatus === 'success' && uploadResult && (
              <div className="mt-6 bg-green-50 border border-green-200 rounded-xl p-6 animate-fade-in">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-green-900 mb-2">
                      Upload Successful!
                    </h3>
                    <p className="text-sm text-green-700 mb-3">
                      Your invoice{uploadResult.invoice_count > 1 ? 's have' : ' has'} been processed successfully.
                    </p>
                    <div className="bg-white rounded-lg p-4 border border-green-200">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Document ID:</span>
                          <p className="font-semibold text-gray-900 mt-1">
                            {uploadResult.document_id || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <span className="text-gray-500">Invoices Found:</span>
                          <p className="font-semibold text-gray-900 mt-1">
                            {uploadResult.invoice_count || 0}
                          </p>
                        </div>
                      </div>
                    </div>
                    <p className="text-xs text-green-600 mt-3">
                      Redirecting to dashboard...
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {uploadStatus === 'error' && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-xl p-6 animate-fade-in">
                <div className="flex items-start space-x-4">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-red-900 mb-2">
                      Upload Failed
                    </h3>
                    <p className="text-sm text-red-700 mb-2">
                      {errorMessage}
                    </p>
                    <button
                      onClick={() => {
                        setUploadStatus(null);
                        setErrorMessage('');
                      }}
                      className="text-sm text-red-600 hover:text-red-800 font-medium underline"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Info Section */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500">
              Supported formats: JPG, PNG, PDF • Maximum file size: 10MB per file
            </p>
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
