import { useState, useEffect } from 'react';
import { Search, Filter, FileText, CheckCircle, AlertCircle, Loader2, RefreshCw } from 'lucide-react';
import InvoiceCard from '../components/InvoiceCard';
import api from '../services/api';

const Dashboard = () => {
  const [invoices, setInvoices] = useState([]);
  const [filteredInvoices, setFilteredInvoices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // 'all' | 'valid' | 'review'
  const [error, setError] = useState(null);

  // Fetch invoices on mount
  useEffect(() => {
    fetchInvoices();
  }, []);

  // Filter invoices when search or filter changes
  useEffect(() => {
    filterInvoicesList();
  }, [searchQuery, filterStatus, invoices]);

  const fetchInvoices = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.getHistory();
      const data = response.data;
      
      // Handle both array and object responses
      const invoiceList = Array.isArray(data) ? data : (data.invoices || []);
      setInvoices(invoiceList);
      setFilteredInvoices(invoiceList);
    } catch (err) {
      console.error('Error fetching invoices:', err);
      setError(err.response?.data?.message || err.message || 'Failed to fetch invoices');
      setInvoices([]);
      setFilteredInvoices([]);
    } finally {
      setIsLoading(false);
    }
  };

  const filterInvoicesList = () => {
    let filtered = [...invoices];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter((invoice) => {
        const searchLower = searchQuery.toLowerCase();
        const firstInvoice = invoice.invoices?.[0] || invoice;
        
        return (
          invoice.document_id?.toLowerCase().includes(searchLower) ||
          firstInvoice.invoice_number?.toLowerCase().includes(searchLower) ||
          firstInvoice.seller_name?.toLowerCase().includes(searchLower) ||
          firstInvoice.buyer_name?.toLowerCase().includes(searchLower)
        );
      });
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter((invoice) => {
        const isValid = invoice.validation_status === 'valid' || invoice.is_valid;
        const hasErrors = invoice.validation_errors?.length > 0;
        
        if (filterStatus === 'valid') {
          return isValid && !hasErrors;
        } else if (filterStatus === 'review') {
          return !isValid || hasErrors;
        }
        return true;
      });
    }

    setFilteredInvoices(filtered);
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteInvoice(id);
      // Remove from state
      setInvoices(invoices.filter(inv => (inv.document_id || inv.id) !== id));
    } catch (err) {
      console.error('Error deleting invoice:', err);
      alert('Failed to delete invoice. Please try again.');
    }
  };

  const handleRefresh = () => {
    fetchInvoices();
  };

  // Calculate statistics
  const stats = {
    total: invoices.length,
    valid: invoices.filter(inv => {
      const isValid = inv.validation_status === 'valid' || inv.is_valid;
      const hasErrors = inv.validation_errors?.length > 0;
      return isValid && !hasErrors;
    }).length,
    review: invoices.filter(inv => {
      const isValid = inv.validation_status === 'valid' || inv.is_valid;
      const hasErrors = inv.validation_errors?.length > 0;
      return !isValid || hasErrors;
    }).length,
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Invoice Dashboard</h1>
          <p className="text-gray-600">Manage and review all processed invoices</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Invoices</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Valid Invoices</p>
                <p className="text-3xl font-bold text-green-600 mt-2">{stats.valid}</p>
              </div>
              <div className="p-3 bg-green-100 rounded-lg">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Need Review</p>
                <p className="text-3xl font-bold text-yellow-600 mt-2">{stats.review}</p>
              </div>
              <div className="p-3 bg-yellow-100 rounded-lg">
                <AlertCircle className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 mb-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 md:space-x-4">
            {/* Search */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by invoice number, seller, buyer..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Filter */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Status</option>
                  <option value="valid">Valid Only</option>
                  <option value="review">Need Review</option>
                </select>
              </div>

              <button
                onClick={handleRefresh}
                disabled={isLoading}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>

        {/* Invoice Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p className="text-gray-600">Loading invoices...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-900 mb-2">Error Loading Invoices</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={handleRefresh}
              className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : filteredInvoices.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-xl p-12 text-center">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {invoices.length === 0 ? 'No Invoices Yet' : 'No Results Found'}
            </h3>
            <p className="text-gray-500 mb-6">
              {invoices.length === 0
                ? 'Upload your first invoice to get started'
                : 'Try adjusting your search or filter criteria'}
            </p>
            {invoices.length === 0 && (
              <a
                href="/"
                className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                Upload Invoice
              </a>
            )}
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              Showing {filteredInvoices.length} of {invoices.length} invoice{invoices.length !== 1 ? 's' : ''}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredInvoices.map((invoice) => (
                <InvoiceCard
                  key={invoice.document_id || invoice.id}
                  invoice={invoice}
                  onDelete={handleDelete}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
