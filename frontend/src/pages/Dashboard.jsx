import { useState, useEffect } from 'react';
import { Search, Filter, FileText, CheckCircle, AlertCircle, Loader2, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const Dashboard = () => {
  const [invoices, setInvoices] = useState([]);
  const [filteredInvoices, setFilteredInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [error, setError] = useState(null);

  // =========================================
  // FETCH INVOICES
  // =========================================
  useEffect(() => {
    fetchInvoices();
  }, []);

  // =========================================
  // FILTER INVOICES
  // =========================================
  useEffect(() => {
    filterInvoicesList();
  }, [searchQuery, filterStatus, invoices]);

  const fetchInvoices = async () => {
    setIsLoading(true);
    setError(null);

    try {
      console.log("Fetching invoices from backend...");

      const response = await fetch("http://127.0.0.1:8000/api/history");

      const result = await response.json();

      console.log("Backend Response:", result);

      const invoiceData = result.data || result;

      console.log("Invoice Data:", invoiceData);

      setInvoices(invoiceData);
      setFilteredInvoices(invoiceData);

    } catch (err) {
      console.error("Error loading invoices:", err);
      setError("Failed to load invoices");
    } finally {
      setIsLoading(false);
    }
  };

  const filterInvoicesList = () => {
    let filtered = [...invoices];

    // =========================================
    // SEARCH FILTER
    // =========================================
    if (searchQuery) {
      filtered = filtered.filter((invoice) => {
        const searchLower = searchQuery.toLowerCase();

        return (
          invoice.document_id?.toLowerCase().includes(searchLower) ||
          invoice.invoice_number?.toLowerCase().includes(searchLower) ||
          invoice.seller_name?.toLowerCase().includes(searchLower) ||
          invoice.buyer_name?.toLowerCase().includes(searchLower)
        );
      });
    }

    // =========================================
    // STATUS FILTER
    // =========================================
    if (filterStatus !== 'all') {
      filtered = filtered.filter((invoice) => {
        if (filterStatus === 'valid') {
          return invoice.validation_status === 'valid';
        }

        if (filterStatus === 'review') {
          return invoice.validation_status !== 'valid';
        }

        return true;
      });
    }

    setFilteredInvoices(filtered);
  };

  // =========================================
  // DELETE
  // =========================================
  const handleDelete = async (id) => {
    try {
      await api.deleteInvoice(id);

      setInvoices(
        invoices.filter(
          inv => (inv.document_id || inv.id) !== id
        )
      );

    } catch (err) {
      console.error('Error deleting invoice:', err);
      alert('Failed to delete invoice');
    }
  };

  // =========================================
  // REFRESH
  // =========================================
  const handleRefresh = () => {
    fetchInvoices();
  };

  // =========================================
  // STATS
  // =========================================
  const stats = {
    total: invoices.length,

    valid: invoices.filter(
      inv => inv.validation_status === "valid"
    ).length,

    review: invoices.filter(
      inv => inv.validation_status !== "valid"
    ).length,
  };

  return (
    <div className="min-h-screen bg-gray-50">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* HEADER */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Invoice Dashboard
          </h1>

          <p className="text-gray-600">
            Manage and review all processed invoices
          </p>
        </div>

        {/* STATS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

          {/* TOTAL */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">

              <div>
                <p className="text-sm font-medium text-gray-600">
                  Total Invoices
                </p>

                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {stats.total}
                </p>
              </div>

              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>

            </div>
          </div>

          {/* VALID */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">

              <div>
                <p className="text-sm font-medium text-gray-600">
                  Valid Invoices
                </p>

                <p className="text-3xl font-bold text-green-600 mt-2">
                  {stats.valid}
                </p>
              </div>

              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>

            </div>
          </div>

          {/* REVIEW */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">

              <div>
                <p className="text-sm font-medium text-gray-600">
                  Need Review
                </p>

                <p className="text-3xl font-bold text-yellow-600 mt-2">
                  {stats.review}
                </p>
              </div>

              <div className="p-3 bg-yellow-100 rounded-lg">
                <AlertCircle className="w-8 h-8 text-yellow-600" />
              </div>

            </div>
          </div>

        </div>

        {/* SEARCH + FILTER */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 mb-8">

          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">

            {/* SEARCH */}
            <div className="flex-1 max-w-md">

              <div className="relative">

                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />

                <input
                  type="text"
                  placeholder="Search invoices..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg"
                />

              </div>

            </div>

            {/* FILTER */}
            <div className="flex items-center space-x-4">

              <div className="flex items-center space-x-2">

                <Filter className="w-5 h-5 text-gray-400" />

                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All Status</option>
                  <option value="valid">Valid Only</option>
                  <option value="review">Need Review</option>
                </select>

              </div>

              {/* REFRESH */}
              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>

            </div>

          </div>

        </div>

        {/* LOADING */}
        {isLoading ? (

          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p>Loading invoices...</p>
          </div>

        ) : error ? (

          <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />

            <h3 className="text-lg font-semibold text-red-900 mb-2">
              Error Loading Invoices
            </h3>

            <p className="text-red-700 mb-4">{error}</p>
          </div>

        ) : filteredInvoices.length === 0 ? (

          <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />

            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Invoices Found
            </h3>
          </div>

        ) : (

          <>
            <div className="mb-4 text-sm text-gray-600">
              Showing {filteredInvoices.length} invoices
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

              {filteredInvoices.map((invoice) => (

                <div
                  key={invoice.document_id}
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-200"
                >

                  <h2 className="text-lg font-bold mb-2">
                    {invoice.invoice_number}
                  </h2>

                  <p className="text-sm text-gray-600 mb-1">
                    Seller: {invoice.seller_name}
                  </p>

                  <p className="text-sm text-gray-600 mb-1">
                    Buyer: {invoice.buyer_name}
                  </p>

                  <p className="text-sm text-gray-600 mb-4">
                    Total: ₹{invoice.total_amount}
                  </p>

                  <div className="flex items-center justify-between">

                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        invoice.validation_status === 'valid'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {invoice.validation_status}
                    </span>

                    <Link
                      to={`/invoice/${invoice.document_id}`}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg"
                    >
                      View Details
                    </Link>

                  </div>

                </div>

              ))}

            </div>
          </>

        )}

      </div>

    </div>
  );
};

export default Dashboard;