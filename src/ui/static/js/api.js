const api = {
    baseUrl: '/api',

    async request(method, path, body = null) {
        const opts = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) opts.body = JSON.stringify(body);

        const res = await fetch(this.baseUrl + path, opts);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        return res.json();
    },

    // --- Pages ---
    getPages() {
        return this.request('GET', '/report-pages/');
    },

    getPageStatus(pageId) {
        return this.request('GET', `/report-pages/${pageId}/status`);
    },

    getPageDetail(pageId) {
        return this.request('GET', `/report-pages/${pageId}/detail`);
    },

    generatePage(pageId, params) {
        return this.request('POST', `/report-pages/${pageId}/generate`, params);
    },

    generateJson(pageId, params) {
        return this.request('POST', `/report-pages/${pageId}/generate-json`, params);
    },

    // --- Reports ---
    getReportPages(reportId) {
        return this.request('GET', `/reports/${reportId}/pages`);
    },

    batchGeneratePages(reportId, params) {
        return this.request('POST', `/reports/${reportId}/generate-pages`, params);
    },

    batchGenerateJson(reportId, params) {
        return this.request('POST', `/reports/${reportId}/generate-json`, params);
    },
};
