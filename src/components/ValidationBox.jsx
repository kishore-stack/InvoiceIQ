import { CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

const ValidationBox = ({ validationData }) => {
  if (!validationData) {
    return null;
  }

  const {
    is_valid,
    validation_status,
    validation_errors = [],
    validation_warnings = [],
    confidence_score,
    validation_details,
  } = validationData;

  const isValid = is_valid || validation_status === 'valid';
  const hasErrors = validation_errors.length > 0;
  const hasWarnings = validation_warnings.length > 0;

  // Determine overall status
  const getStatusConfig = () => {
    if (isValid && !hasErrors && !hasWarnings) {
      return {
        status: 'success',
        icon: CheckCircle,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        iconColor: 'text-green-600',
        textColor: 'text-green-800',
        title: 'Validation Passed',
        message: 'All invoice data has been validated successfully.',
      };
    } else if (hasErrors) {
      return {
        status: 'error',
        icon: XCircle,
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        iconColor: 'text-red-600',
        textColor: 'text-red-800',
        title: 'Validation Failed',
        message: 'Invoice contains validation errors that need attention.',
      };
    } else if (hasWarnings) {
      return {
        status: 'warning',
        icon: AlertTriangle,
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        iconColor: 'text-yellow-600',
        textColor: 'text-yellow-800',
        title: 'Validation Warning',
        message: 'Invoice validation completed with warnings.',
      };
    } else {
      return {
        status: 'info',
        icon: Info,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        iconColor: 'text-blue-600',
        textColor: 'text-blue-800',
        title: 'Validation Complete',
        message: 'Invoice has been processed.',
      };
    }
  };

  const config = getStatusConfig();
  const StatusIcon = config.icon;

  return (
    <div className="space-y-4">
      {/* Main Status Card */}
      <div className={`${config.bgColor} border ${config.borderColor} rounded-xl p-6`}>
        <div className="flex items-start space-x-4">
          <div className={`p-2 bg-white rounded-lg shadow-sm`}>
            <StatusIcon className={`w-6 h-6 ${config.iconColor}`} />
          </div>
          <div className="flex-1">
            <h3 className={`text-lg font-semibold ${config.textColor}`}>
              {config.title}
            </h3>
            <p className={`text-sm mt-1 ${config.textColor} opacity-90`}>
              {config.message}
            </p>

            {/* Confidence Score */}
            {confidence_score !== undefined && (
              <div className="mt-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className={config.textColor}>Confidence Score</span>
                  <span className={`font-semibold ${config.textColor}`}>
                    {Math.round(confidence_score)}%
                  </span>
                </div>
                <div className="w-full bg-white bg-opacity-50 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      confidence_score >= 80
                        ? 'bg-green-500'
                        : confidence_score >= 60
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${confidence_score}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Validation Errors */}
      {hasErrors && (
        <div className="bg-white border border-red-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <XCircle className="w-5 h-5 text-red-600" />
            <h4 className="font-semibold text-gray-900">
              Validation Errors ({validation_errors.length})
            </h4>
          </div>
          <ul className="space-y-2">
            {validation_errors.map((error, index) => (
              <li key={index} className="flex items-start space-x-2 text-sm">
                <span className="text-red-500 mt-0.5">•</span>
                <span className="text-gray-700 flex-1">
                  {typeof error === 'string' ? error : error.message || JSON.stringify(error)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Validation Warnings */}
      {hasWarnings && (
        <div className="bg-white border border-yellow-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <h4 className="font-semibold text-gray-900">
              Warnings ({validation_warnings.length})
            </h4>
          </div>
          <ul className="space-y-2">
            {validation_warnings.map((warning, index) => (
              <li key={index} className="flex items-start space-x-2 text-sm">
                <span className="text-yellow-500 mt-0.5">•</span>
                <span className="text-gray-700 flex-1">
                  {typeof warning === 'string' ? warning : warning.message || JSON.stringify(warning)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Validation Details */}
      {validation_details && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h4 className="font-semibold text-gray-900 mb-4">Validation Details</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(validation_details).map(([key, value]) => (
              <div key={key} className="text-sm">
                <span className="text-gray-500 capitalize">
                  {key.replace(/_/g, ' ')}:
                </span>
                <span className="ml-2 text-gray-900 font-medium">
                  {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ValidationBox;
