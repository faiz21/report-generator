function truncate(str, len) {
    if (!str) return '-';
    return str.length > len ? str.slice(0, len) + '...' : str;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

const STATUS_CONFIG = {
    completed:            { label: 'Completed',       color: 'bg-green-100 text-green-700',  dot: 'bg-green-500' },
    generating_draft:     { label: 'Generating',      color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500 pulse-dot' },
    draft_generated:      { label: 'Draft Ready',     color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500' },
    validating_outline:   { label: 'Validating',      color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500 pulse-dot' },
    validation_completed: { label: 'Validated',        color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500' },
    refining_content:     { label: 'Refining',        color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500 pulse-dot' },
    content_refined:      { label: 'Refined',         color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500' },
    translating:          { label: 'Translating',     color: 'bg-indigo-100 text-indigo-700', dot: 'bg-indigo-500 pulse-dot' },
    translated:           { label: 'Translated',      color: 'bg-indigo-100 text-indigo-700', dot: 'bg-indigo-500' },
    analyzing:            { label: 'Analyzing',       color: 'bg-purple-100 text-purple-700', dot: 'bg-purple-500 pulse-dot' },
    analysis_completed:   { label: 'Analyzed',        color: 'bg-purple-100 text-purple-700', dot: 'bg-purple-500' },
    persisting_outputs:   { label: 'Saving',          color: 'bg-yellow-100 text-yellow-700', dot: 'bg-yellow-500 pulse-dot' },
    vectorizing:          { label: 'Vectorizing',     color: 'bg-yellow-100 text-yellow-700', dot: 'bg-yellow-500 pulse-dot' },
    failed:               { label: 'Failed',          color: 'bg-red-100 text-red-700',      dot: 'bg-red-500' },
    partial_failed:       { label: 'Partial',         color: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500' },
    queued:               { label: 'Queued',          color: 'bg-gray-100 text-gray-600',    dot: 'bg-gray-400 pulse-dot' },
    json_pending:         { label: 'Pending',         color: 'bg-gray-100 text-gray-600',    dot: 'bg-gray-400' },
    json_generating:      { label: 'Generating',      color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500 pulse-dot' },
    json_validating:      { label: 'Validating',      color: 'bg-blue-100 text-blue-700',    dot: 'bg-blue-500 pulse-dot' },
    json_persisted:       { label: 'Done',            color: 'bg-green-100 text-green-700',  dot: 'bg-green-500' },
    json_failed:          { label: 'Failed',          color: 'bg-red-100 text-red-700',      dot: 'bg-red-500' },
};

function statusBadge(status, type) {
    if (!status) return '<span class="text-xs text-gray-400">-</span>';
    const cfg = STATUS_CONFIG[status] || { label: status, color: 'bg-gray-100 text-gray-600', dot: 'bg-gray-400' };
    return `<span class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}">
        <span class="h-1.5 w-1.5 rounded-full ${cfg.dot}"></span>
        ${cfg.label}
    </span>`;
}

function scoreBadge(score) {
    if (score == null) return '<span class="text-xs text-gray-400">-</span>';
    const s = parseFloat(score);
    const color = s >= 80 ? 'text-green-700 bg-green-50' : s >= 60 ? 'text-yellow-700 bg-yellow-50' : 'text-red-700 bg-red-50';
    return `<span class="inline-flex rounded-md px-2 py-0.5 text-xs font-bold ${color}">${s.toFixed(1)}</span>`;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const colors = {
        success: 'bg-green-600',
        error: 'bg-red-600',
        info: 'bg-gray-800',
    };
    const toast = document.createElement('div');
    toast.className = `${colors[type] || colors.info} text-white px-4 py-2.5 rounded-lg shadow-lg text-sm font-medium fade-in max-w-xs`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
