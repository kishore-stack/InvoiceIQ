import { Link } from "react-router-dom";
import { FileText, Eye, Trash2, Building2, DollarSign } from "lucide-react";

const InvoiceCard = ({ invoice, onDelete }) => {
  const invoiceData = invoice.invoices?.[0] || invoice;

  const documentId = invoice.document_id || invoiceData.document_id || invoice.id;
  const invoiceNumber = invoiceData.invoice_number || "N/A";
  const sellerName = invoiceData.seller_name || "N/A";
  const buyerName = invoiceData.buyer_name || "N/A";
  const totalAmount = invoiceData.total_amount;

  const validation = invoiceData.validation || invoice.validation || {};
  const isValid =
    validation.validation_status === true ||
    validation.validation_status === "valid" ||
    invoice.validation_status === "valid" ||
    invoice.is_valid === true;

  const confidenceScore =
    invoiceData.confidence_score || invoice.confidence_score || 0;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-5">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <FileText className="w-7 h-7 text-blue-600" />
          </div>

          <div>
            <h3 className="text-xl font-bold text-gray-900">
              {invoiceNumber}
            </h3>
            <p className="text-sm text-gray-500">{documentId}</p>
          </div>
        </div>

        <span
          className={`px-3 py-1 text-xs font-medium rounded-full ${
            isValid
              ? "bg-green-100 text-green-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          {isValid ? "Valid" : "Review"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <div>
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
            <Building2 className="w-4 h-4" />
            <span>Seller</span>
          </div>
          <p className="font-semibold text-gray-900">{sellerName}</p>
        </div>

        <div>
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
            <Building2 className="w-4 h-4" />
            <span>Buyer</span>
          </div>
          <p className="font-semibold text-gray-900">{buyerName}</p>
        </div>
      </div>

      <div className="mb-5">
        <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
          <DollarSign className="w-4 h-4" />
          <span>Total Amount</span>
        </div>

        <p className="font-bold text-gray-900">
          {totalAmount != null
            ? `₹${Number(totalAmount).toLocaleString()}`
            : "Not Extracted"}
        </p>
      </div>

      <div className="mb-5">
        <div className="flex justify-between text-sm mb-2">
          <span className="text-gray-600">Confidence Score</span>
          <span className="font-semibold text-gray-900">
            {confidenceScore}%
          </span>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full"
            style={{ width: `${confidenceScore}%` }}
          />
        </div>
      </div>

      <div className="flex gap-3">
        <Link
          to={`/invoice/${documentId}`}
          className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-colors"
        >
          <Eye className="w-4 h-4" />
          View Details
        </Link>

        <button
          onClick={() => onDelete(documentId)}
          className="px-4 py-3 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors"
        >
          <Trash2 className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default InvoiceCard;