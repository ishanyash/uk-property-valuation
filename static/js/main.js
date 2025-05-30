// Main JavaScript for the Property Valuation App

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const addressForm = document.getElementById('address-form');
    const addressInput = document.getElementById('address-input');
    const generateBtn = document.getElementById('generate-btn');
    const progressSection = document.getElementById('progress-section');
    const progressBar = document.getElementById('progress-bar');
    const progressMessage = document.getElementById('progress-message');
    const agentStatusContainer = document.getElementById('agent-status-container');
    
    // Agent status elements
    const researchStatus = document.getElementById('research-status');
    const evaluationStatus = document.getElementById('evaluation-status');
    const accessorStatus = document.getElementById('accessor-status');
    const reportStatus = document.getElementById('report-status');
    
    // Error handling
    let errorRetries = 0;
    const MAX_RETRIES = 3;
    
    // Hide progress section initially
    progressSection.style.display = 'none';
    
    // Form submission
    addressForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const address = addressInput.value.trim();
        
        if (!address) {
            showError('Please enter a UK address');
            return;
        }
        
        // Validate address
        validateAddress(address);
    });
    
    // Validate address
    function validateAddress(address) {
        fetch('/validate-address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address: address })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                if (data.warning) {
                    showWarning(data.warning);
                }
                generateReport(data.formatted_address || address);
            } else {
                showError(data.message || 'Invalid address');
            }
        })
        .catch(error => {
            console.error('Error validating address:', error);
            showError('Error validating address. Please try again.');
        });
    }
    
    // Generate report
    function generateReport(address) {
        // Reset UI
        resetProgress();
        
        // Show progress section
        progressSection.style.display = 'block';
        
        // Disable form
        addressInput.disabled = true;
        generateBtn.disabled = true;
        
        // Update progress
        updateProgress(10, 'Starting report generation...');
        updateAgentStatus('research', 'pending', 'Initializing...');
        
        // Send request to generate report
        fetch('/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address: address })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Start polling for status
                pollReportStatus(data.report_id);
            } else {
                showError(data.message || 'Failed to start report generation');
                resetForm();
            }
        })
        .catch(error => {
            console.error('Error generating report:', error);
            showError('Error generating report. Please try again.');
            resetForm();
        });
    }
    
    // Poll report status
    function pollReportStatus(reportId) {
        const statusUrl = `/report-status/${reportId}`;
        
        // Function to check status
        function checkStatus() {
            fetch(statusUrl)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update progress
                        updateProgress(data.progress, data.message);
                        
                        // Update agent statuses based on current stage
                        updateAgentStatusesFromProgress(data.status, data.message, data.agent_details || {});
                        
                        if (data.complete) {
                            // Report is complete, redirect to view
                            window.location.href = `/view-report/${reportId}`;
                        } else if (data.status === 'error') {
                            // Show error and reset form
                            showError(data.message || 'An error occurred during report generation');
                            
                            // Show detailed error if available
                            if (data.error_details) {
                                showDetailedError(data.error_details);
                            }
                            
                            // Enable retry if appropriate
                            if (data.can_retry && errorRetries < MAX_RETRIES) {
                                errorRetries++;
                                showRetryOption(reportId);
                            } else {
                                resetForm();
                            }
                        } else {
                            // Continue polling
                            setTimeout(checkStatus, 2000);
                        }
                    } else {
                        showError(data.message || 'Failed to check report status');
                        resetForm();
                    }
                })
                .catch(error => {
                    console.error('Error checking report status:', error);
                    
                    // Implement exponential backoff for polling errors
                    const backoffDelay = Math.min(1000 * Math.pow(2, errorRetries), 10000);
                    errorRetries++;
                    
                    if (errorRetries <= MAX_RETRIES) {
                        updateProgress(data.progress, `Connection issue. Retrying in ${backoffDelay/1000} seconds...`);
                        setTimeout(checkStatus, backoffDelay);
                    } else {
                        showError('Failed to check report status after multiple attempts');
                        resetForm();
                    }
                });
        }
        
        // Start checking status
        checkStatus();
    }
    
    // Update progress bar and message
    function updateProgress(percent, message) {
        progressBar.style.width = `${percent}%`;
        progressBar.setAttribute('aria-valuenow', percent);
        progressMessage.textContent = message || '';
    }
    
    // Update agent statuses based on current progress stage
    function updateAgentStatusesFromProgress(status, message, agentDetails) {
        // Reset all to pending first
        if (status === 'researching') {
            updateAgentStatus('research', 'active', agentDetails.research || 'Gathering property data...');
            updateAgentStatus('evaluation', 'pending', 'Waiting...');
            updateAgentStatus('accessor', 'pending', 'Waiting...');
            updateAgentStatus('report', 'pending', 'Waiting...');
        } 
        else if (status === 'evaluating') {
            updateAgentStatus('research', 'complete', 'Research complete');
            updateAgentStatus('evaluation', 'active', agentDetails.evaluation || 'Analyzing property data...');
            updateAgentStatus('accessor', 'pending', 'Waiting...');
            updateAgentStatus('report', 'pending', 'Waiting...');
        }
        else if (status === 'reviewing') {
            updateAgentStatus('research', 'complete', 'Research complete');
            updateAgentStatus('evaluation', 'complete', 'Evaluation complete');
            updateAgentStatus('accessor', 'active', agentDetails.accessor || 'Reviewing and approving data...');
            updateAgentStatus('report', 'pending', 'Waiting...');
        }
        else if (status === 'generating') {
            updateAgentStatus('research', 'complete', 'Research complete');
            updateAgentStatus('evaluation', 'complete', 'Evaluation complete');
            updateAgentStatus('accessor', 'complete', 'Review complete');
            updateAgentStatus('report', 'active', agentDetails.report || 'Generating report...');
        }
        else if (status === 'complete') {
            updateAgentStatus('research', 'complete', 'Research complete');
            updateAgentStatus('evaluation', 'complete', 'Evaluation complete');
            updateAgentStatus('accessor', 'complete', 'Review complete');
            updateAgentStatus('report', 'complete', 'Report complete');
        }
        else if (status === 'error') {
            // Find which agent had the error
            if (agentDetails.error_agent) {
                const errorAgent = agentDetails.error_agent;
                
                if (errorAgent === 'research') {
                    updateAgentStatus('research', 'error', agentDetails.error_message || 'Error in research');
                    updateAgentStatus('evaluation', 'pending', 'Not started');
                    updateAgentStatus('accessor', 'pending', 'Not started');
                    updateAgentStatus('report', 'pending', 'Not started');
                }
                else if (errorAgent === 'evaluation') {
                    updateAgentStatus('research', 'complete', 'Research complete');
                    updateAgentStatus('evaluation', 'error', agentDetails.error_message || 'Error in evaluation');
                    updateAgentStatus('accessor', 'pending', 'Not started');
                    updateAgentStatus('report', 'pending', 'Not started');
                }
                else if (errorAgent === 'accessor') {
                    updateAgentStatus('research', 'complete', 'Research complete');
                    updateAgentStatus('evaluation', 'complete', 'Evaluation complete');
                    updateAgentStatus('accessor', 'error', agentDetails.error_message || 'Error in review');
                    updateAgentStatus('report', 'pending', 'Not started');
                }
                else if (errorAgent === 'report_generator') {
                    updateAgentStatus('research', 'complete', 'Research complete');
                    updateAgentStatus('evaluation', 'complete', 'Evaluation complete');
                    updateAgentStatus('accessor', 'complete', 'Review complete');
                    updateAgentStatus('report', 'error', agentDetails.error_message || 'Error in report generation');
                }
            } else {
                // Generic error handling if agent not specified
                updateAgentStatus('research', 'unknown', '');
                updateAgentStatus('evaluation', 'unknown', '');
                updateAgentStatus('accessor', 'unknown', '');
                updateAgentStatus('report', 'unknown', '');
            }
        }
    }
    
    // Update individual agent status
    function updateAgentStatus(agent, status, message) {
        let statusElement;
        
        switch(agent) {
            case 'research':
                statusElement = researchStatus;
                break;
            case 'evaluation':
                statusElement = evaluationStatus;
                break;
            case 'accessor':
                statusElement = accessorStatus;
                break;
            case 'report':
                statusElement = reportStatus;
                break;
            default:
                return;
        }
        
        // Remove all status classes
        statusElement.classList.remove('pending', 'active', 'complete', 'error', 'unknown');
        
        // Add appropriate class
        statusElement.classList.add(status);
        
        // Update message if provided
        if (message) {
            statusElement.textContent = message;
        }
    }
    
    // Reset progress UI
    function resetProgress() {
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        progressMessage.textContent = '';
        errorRetries = 0;
        
        // Reset agent statuses
        updateAgentStatus('research', 'pending', 'Waiting...');
        updateAgentStatus('evaluation', 'pending', 'Waiting...');
        updateAgentStatus('accessor', 'pending', 'Waiting...');
        updateAgentStatus('report', 'pending', 'Waiting...');
    }
    
    // Reset form
    function resetForm() {
        addressInput.disabled = false;
        generateBtn.disabled = false;
    }
    
    // Show error message
    function showError(message) {
        // Create error alert
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show mt-3';
        errorAlert.role = 'alert';
        errorAlert.innerHTML = `
            <strong>Error:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to page
        addressForm.insertAdjacentElement('afterend', errorAlert);
        
        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            errorAlert.classList.remove('show');
            setTimeout(() => errorAlert.remove(), 500);
        }, 10000);
    }
    
    // Show warning message
    function showWarning(message) {
        // Create warning alert
        const warningAlert = document.createElement('div');
        warningAlert.className = 'alert alert-warning alert-dismissible fade show mt-3';
        warningAlert.role = 'alert';
        warningAlert.innerHTML = `
            <strong>Warning:</strong> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to page
        addressForm.insertAdjacentElement('afterend', warningAlert);
        
        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            warningAlert.classList.remove('show');
            setTimeout(() => warningAlert.remove(), 500);
        }, 10000);
    }
    
    // Show detailed error information
    function showDetailedError(errorDetails) {
        // Create detailed error modal
        const modalId = 'errorDetailsModal';
        let modal = document.getElementById(modalId);
        
        // Remove existing modal if present
        if (modal) {
            modal.remove();
        }
        
        // Create new modal
        modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = modalId;
        modal.tabIndex = '-1';
        modal.setAttribute('aria-labelledby', `${modalId}Label`);
        modal.setAttribute('aria-hidden', 'true');
        
        // Format error details
        let errorContent = '';
        if (typeof errorDetails === 'string') {
            errorContent = errorDetails;
        } else if (typeof errorDetails === 'object') {
            errorContent = `<pre>${JSON.stringify(errorDetails, null, 2)}</pre>`;
        }
        
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-danger text-white">
                        <h5 class="modal-title" id="${modalId}Label">Error Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="error-details">
                            ${errorContent}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(modal);
        
        // Show modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }
    
    // Show retry option
    function showRetryOption(reportId) {
        // Create retry alert
        const retryAlert = document.createElement('div');
        retryAlert.className = 'alert alert-warning mt-3';
        retryAlert.innerHTML = `
            <p><strong>Error encountered:</strong> Would you like to retry?</p>
            <button id="retry-btn" class="btn btn-warning">Retry</button>
            <button id="cancel-btn" class="btn btn-outline-secondary ms-2">Cancel</button>
        `;
        
        // Add to page
        progressSection.insertAdjacentElement('afterend', retryAlert);
        
        // Add event listeners
        document.getElementById('retry-btn').addEventListener('click', function() {
            retryAlert.remove();
            pollReportStatus(reportId);
        });
        
        document.getElementById('cancel-btn').addEventListener('click', function() {
            retryAlert.remove();
            resetForm();
        });
    }
});
