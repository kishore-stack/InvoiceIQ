const ResultTable = ({ items = [] }) => {
  if (!items || items.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500">No line items found</p>
      </div>
    );
  }

  // Calculate totals
  const calculateSubtotal = () => {
    return items.reduce((sum, item) => {
      const price = parseFloat(item.price || item.unit_price || 0);
      const qty = parseFloat(item.quantity || 1);
      return sum + (price * qty);
    }, 0);
  };

  const calculateTotalTax = () => {
    return items.reduce((sum, item) => {
      return sum + parseFloat(item.tax || item.tax_amount || 0);
    }, 0);
  };

  const calculateTotalDiscount = () => {
    return items.reduce((sum, item) => {
      return sum + parseFloat(item.discount || 0);
    }, 0);
  };

  const subtotal = calculateSubtotal();
  const totalTax = calculateTotalTax();
  const totalDiscount = calculateTotalDiscount();
  const grandTotal = subtotal + totalTax - totalDiscount;

  return (
    <div className="w-full overflow-hidden border border-gray-200 rounded-xl bg-white shadow-sm">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                #
              </th>
              <th scope="col" className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Description
              </th>
              <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Quantity
              </th>
              <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Unit Price
              </th>
              <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Tax
              </th>
              <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Discount
              </th>
              <th scope="col" className="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Total
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((item, index) => {
              const price = parseFloat(item.price || item.unit_price || 0);
              const qty = parseFloat(item.quantity || 1);
              const tax = parseFloat(item.tax || item.tax_amount || 0);
              const discount = parseFloat(item.discount || 0);
              const total = (price * qty) + tax - discount;

              return (
                <tr key={index} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {index + 1}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="max-w-xs">
                      <p className="font-medium">{item.description || item.item_name || 'N/A'}</p>
                      {item.item_code && (
                        <p className="text-xs text-gray-500 mt-1">Code: {item.item_code}</p>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-medium">
                    {qty}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    ${price.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {tax > 0 ? `$${tax.toFixed(2)}` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    {discount > 0 ? `$${discount.toFixed(2)}` : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-semibold">
                    ${total.toFixed(2)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Summary Section */}
      <div className="bg-gray-50 border-t border-gray-200 px-6 py-4">
        <div className="max-w-md ml-auto space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Subtotal:</span>
            <span className="font-medium text-gray-900">${subtotal.toFixed(2)}</span>
          </div>
          
          {totalTax > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Tax:</span>
              <span className="font-medium text-gray-900">${totalTax.toFixed(2)}</span>
            </div>
          )}
          
          {totalDiscount > 0 && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Discount:</span>
              <span className="font-medium text-red-600">-${totalDiscount.toFixed(2)}</span>
            </div>
          )}
          
          <div className="flex justify-between text-base pt-2 border-t border-gray-300">
            <span className="font-semibold text-gray-900">Grand Total:</span>
            <span className="font-bold text-gray-900 text-lg">${grandTotal.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultTable;
