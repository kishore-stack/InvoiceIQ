import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const InvoiceDetails = () => {
  const { id } = useParams();

  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvoice();
  }, []);

  const fetchInvoice = async () => {
    try {
      console.log("Invoice ID:", id);

      // Direct fetch API
      const response = await fetch("http://127.0.0.1:8000/api/history");

      const result = await response.json();

      console.log("API Result:", result);

      // Backend returns {status,count,data}
      const invoices = result.data || [];

      console.log("Invoices:", invoices);

      const foundInvoice = invoices.find(
        (inv) =>
          String(inv.document_id) === String(id) ||
          String(inv.id) === String(id)
      );

      console.log("Found Invoice:", foundInvoice);

      setInvoice(foundInvoice);

    } catch (error) {
      console.error("Error fetching invoice:", error);
    } finally {
      setLoading(false);
    }
  };

  // Loading
  if (loading) {
    return (
      <div className="p-10 text-lg">
        Loading...
      </div>
    );
  }

  // Not Found
  if (!invoice) {
    return (
      <div className="p-10 text-red-600 text-xl">
        Invoice not found
      </div>
    );
  }

  // Success
  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">
        Invoice Details
      </h1>

      <div className="bg-white shadow-lg rounded-xl p-6 space-y-3">
        <p>
          <strong>Document ID:</strong> {invoice.document_id}
        </p>

        <p>
          <strong>Invoice Number:</strong> {invoice.invoice_number}
        </p>

        <p>
          <strong>Date:</strong> {invoice.date}
        </p>

        <p>
          <strong>Seller:</strong> {invoice.seller_name}
        </p>

        <p>
          <strong>Buyer:</strong> {invoice.buyer_name}
        </p>

        <p>
          <strong>Subtotal:</strong> ₹{invoice.subtotal}
        </p>

        <p>
          <strong>Tax Amount:</strong> ₹{invoice.tax_amount}
        </p>

        <p>
          <strong>Total Amount:</strong> ₹{invoice.total_amount}
        </p>

        <p>
          <strong>Status:</strong> {invoice.validation_status}
        </p>

        <p>
          <strong>Created At:</strong> {invoice.created_at}
        </p>
      </div>
    </div>
  );
};

export default InvoiceDetails;