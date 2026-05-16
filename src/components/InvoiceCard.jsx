import { useNavigate } from 'react-router-dom';
import { FileText, Eye, Trash2, CheckCircle, AlertCircle, Calendar, Building2, DollarSign } from 'lucide-react';

const InvoiceCard = ({ invoice, onDelete }) => {
  const navigate = useNavigate();

  const handleView = () => {
    navigate(`/invoice/${invoice.document_id || invoice.id}`);
  };

  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this invoice?')) {
      onDelete(invoice.document_id || invoice.id);
    }
  };

  // Get validation status
  const isValid = invoice.validation_status === 'valid' || invoice.is_valid;
  const hasErrors = invoice.validation_errors && invoice.validation_errors.length > 0;

  // Get first invoice data if multiple invoices in document
  const firstInvoice = invoice.invoices && invoice.invoices.length > 0 
    ? invoice.invoices[0] 
    : invoice;

  return (
    <div
      className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group"
      onClick={handleView}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg group-hover:from-blue-200 group-hover:to-indigo-200 transition-colors">
            <FileText className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 text-lg">
              {firstInvoice.invoice_number || 'N/A'}
            </h3>
            <p className="text-sm text-gray-500">
              {invoice.document_id || invoice.id || 'Unknown ID'}
            </p>
          </div>
        </div>

        {/* Status Badge */}
        <div className="flex items-center space-x-2">
          {isValid && !hasErrors ? (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <CheckCircle className="w-3 h-3 mr-1" />
              Valid
            </span>
          ) : (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              <AlertCircle className="w-3 h-3 mr-1" />
              Review
            </span>
          )}
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Seller */}
        {firstInvoice.seller_name && (
          <div className="flex items-start space-x-2">
            <Building2 className="w-4 h-4 text-gray-400 mt-0.5" />
            <div className="min-w-0 flex-1">
              <p className="text-xs text-gray-500">Seller</p>
              <p className="text-sm font-medium text-gray-900 truncate">
                {firstInvoice.seller_name}
              </p>
            </div>
          </div>
        )}

        {/* Buyer */}
        {firstInvoice.buyer_name && (
          <div className="flex items-start space-x-2">
            <Building2 className="w-4 h-4 text-gray-400 mt-0.5" />
            <div className="min-w-0 flex-1">
              <p className="text-xs text-gray-500">Buyer</p>
              <p className="text-sm font-medium text-gray-900 truncate">
                {firstInvoice.buyer_name}
              </p>
            </div>
          </div>
        )}

        {/* Total Amount */}
        {firstInvoice.total_amount !== undefined && (
          <div className="flex items-start space-x-2">
            <DollarSign className="w-4 h-4 text-gray-400 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500">Total Amount</p>
              <p className="text-sm font-medium text-gray-900">
                ${firstInvoice.total_amount?.toLocaleString() || '0.00'}
              </p>
            </div>
          </div>
        )}

        {/* Date */}
        {(invoice.created_at || invoice.date) && (
          <div className="flex items-start space-x-2">
            <Calendar className="w-4 h-4 text-gray-400 mt-0.5" />
            <div>
              <p className="text-xs text-gray-500">Date</p>
              <p className="text-sm font-medium text-gray-900">
                {new Date(invoice.created_at || invoice.date).toLocaleDateString()}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Invoice Count */}
      {invoice.invoice_count > 1 && (
        <div className="mb-4">
          <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700">
            {invoice.invoice_count} invoices in document
          </span>
        </div>
      )}

      {/* Confidence Score */}
      {firstInvoice.confidence_score !== undefined && (
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
            <span>Confidence Score</span>
            <span className="font-medium">{Math.round(firstInvoice.confidence_score)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all ${
                firstInvoice.confidence_score >= 80
                  ? 'bg-green-500'
                  : firstInvoice.confidence_score >= 60
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${firstInvoice.confidence_score}%` }}
            />
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center space-x-2 pt-4 border-t border-gray-100">
        <button
          onClick={handleView}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center space-x-2"
        >
          <Eye className="w-4 h-4" />
          <span>View Details</span>
        </button>
        <button
          onClick={handleDelete}
          className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 text-sm font-medium rounded-lg transition-colors"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default InvoiceCard;
