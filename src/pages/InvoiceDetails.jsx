import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  FileText, 
  Building2, 
  Calendar, 
  Hash, 
  DollarSign,
  Loader2,
  Download,
  Trash2
} from 'lucide-react';
import ResultTable from '../components/ResultTable';
import ValidationBox from '../components/ValidationBox';
import api from '../services/api';

const InvoiceDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchInvoiceDetails();
  }, [id]);

  const fetchInvoiceDetails = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getInvoice(id);
      setInvoice(response.data);
    } catch (err) {
      console.error('Error fetching invoice details:', err);
      setError(err.response?.data?.message || err.message || 'Failed to fetch invoice details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this invoice?')) {
      try {
        await api.deleteInvoice(id);
        navigate('/dashboard');
      } catch (err) {
        console.error('Error deleting invoice:', err);
        alert('Failed to delete invoice. Please try again.');
      }
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading invoice details...</p>
        </div>
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <button
            onClick={handleBack}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
          
          <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <FileText className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-red-900 mb-2">Invoice Not Found</h2>
            <p className="text-red-700 mb-6">{error || 'The requested invoice could not be found.'}</p>
            <button
              onClick={handleBack}
              className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Get first invoice if multiple in document
  const invoiceData = invoice.invoices?.[0] || invoice;
  const allInvoices = invoice.invoices || [invoice];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={handleBack}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Dashboard</span>
          </button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Invoice Details</h1>
              <p className="text-gray-600">Document ID: {invoice.document_id || id}</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => window.print()}
                className="px-4 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg transition-colors flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export</span>
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center space-x-2"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>

        {/* Validation Status */}
        <div className="mb-8">
          <ValidationBox validationData={invoice} />
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {allInvoices.map((inv, index) => (
            <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              {/* Invoice Header */}
              {allInvoices.length > 1 && (
                <div className="bg-blue-50 border-b border-blue-100 px-6 py-3">
                  <h3 className="font-semibold text-blue-900">
                    Invoice {index + 1} of {allInvoices.length}
                  </h3>
                </div>
              )}

              <div className="p-6 space-y-6">
                {/* Basic Information */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-blue-600" />
                    Invoice Information
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Invoice Number */}
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2 text-gray-500">
                        <Hash className="w-4 h-4" />
                        <span className="text-sm font-medium">Invoice Number</span>
                      </div>
                      <p className="text-lg font-semibold text-gray-900">
                        {inv.invoice_number || 'N/A'}
                      </p>
                    </div>

                    {/* Date */}
                    {inv.date && (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-gray-500">
                          <Calendar className="w-4 h-4" />
                          <span className="text-sm font-medium">Invoice Date</span>
                        </div>
                        <p className="text-lg font-semibold text-gray-900">
                          {new Date(inv.date).toLocaleDateString()}
                        </p>
                      </div>
                    )}

                    {/* Total Amount */}
                    {inv.total_amount !== undefined && (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-gray-500">
                          <DollarSign className="w-4 h-4" />
                          <span className="text-sm font-medium">Total Amount</span>
                        </div>
                        <p className="text-2xl font-bold text-blue-600">
                          ${inv.total_amount?.toLocaleString() || '0.00'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Parties */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Seller */}
                  {inv.seller_name && (
                    <div className="bg-gray-50 rounded-lg p-6">
                      <div className="flex items-center space-x-2 text-gray-700 mb-3">
                        <Building2 className="w-5 h-5" />
                        <h4 className="font-semibold">Seller Information</h4>
                      </div>
                      <div className="space-y-2 text-sm">
                        <p className="font-medium text-gray-900">{inv.seller_name}</p>
                        {inv.seller_address && (
                          <p className="text-gray-600">{inv.seller_address}</p>
                        )}
                        {inv.seller_gst && (
                          <p className="text-gray-600">GST: {inv.seller_gst}</p>
                        )}
                        {inv.seller_contact && (
                          <p className="text-gray-600">{inv.seller_contact}</p>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Buyer */}
                  {inv.buyer_name && (
                    <div className="bg-gray-50 rounded-lg p-6">
                      <div className="flex items-center space-x-2 text-gray-700 mb-3">
                        <Building2 className="w-5 h-5" />
                        <h4 className="font-semibold">Buyer Information</h4>
                      </div>
                      <div className="space-y-2 text-sm">
                        <p className="font-medium text-gray-900">{inv.buyer_name}</p>
                        {inv.buyer_address && (
                          <p className="text-gray-600">{inv.buyer_address}</p>
                        )}
                        {inv.buyer_gst && (
                          <p className="text-gray-600">GST: {inv.buyer_gst}</p>
                        )}
                        {inv.buyer_contact && (
                          <p className="text-gray-600">{inv.buyer_contact}</p>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Line Items */}
                {inv.line_items && inv.line_items.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Line Items
                    </h3>
                    <ResultTable items={inv.line_items} />
                  </div>
                )}

                {/* Additional Financial Info */}
                {(inv.subtotal || inv.tax_amount || inv.discount) && (
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h4 className="font-semibold text-gray-900 mb-4">Financial Summary</h4>
                    <div className="space-y-2 max-w-md ml-auto">
                      {inv.subtotal !== undefined && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Subtotal:</span>
                          <span className="font-medium">${inv.subtotal.toFixed(2)}</span>
                        </div>
                      )}
                      {inv.tax_amount !== undefined && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Tax:</span>
                          <span className="font-medium">${inv.tax_amount.toFixed(2)}</span>
                        </div>
                      )}
                      {inv.discount !== undefined && inv.discount > 0 && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Discount:</span>
                          <span className="font-medium text-red-600">-${inv.discount.toFixed(2)}</span>
                        </div>
                      )}
                      {inv.total_amount !== undefined && (
                        <div className="flex justify-between text-base pt-2 border-t border-gray-300">
                          <span className="font-semibold">Total Amount:</span>
                          <span className="font-bold text-lg">${inv.total_amount.toFixed(2)}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Raw Data (for debugging) */}
                {inv.raw_text && (
                  <details className="bg-gray-50 rounded-lg p-6">
                    <summary className="font-semibold text-gray-900 cursor-pointer">
                      Raw OCR Text
                    </summary>
                    <pre className="mt-4 text-xs text-gray-600 whitespace-pre-wrap bg-white p-4 rounded border border-gray-200 max-h-64 overflow-y-auto">
                      {inv.raw_text}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default InvoiceDetails;
