class JourneyTracker {
    constructor(apiKey, baseUrl = 'http://localhost:3000/api/v1') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.sessionId = this.generateSessionId();
    }

    // Generate a unique session ID
    generateSessionId() {
        return 'sess_' + Math.random().toString(36).substr(2, 9);
    }

    // Track a user event
    async trackEvent(eventName, metadata = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/track`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': this.apiKey
                },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    eventName,
                    metadata
                })
            });

            const data = await response.json();
            if (!data.success) {
                console.error('Error tracking event:', data.error);
            }
            return data;
        } catch (error) {
            console.error('Error tracking event:', error);
            return { success: false, error: error.message };
        }
    }

    // Get current journey stage
    async getJourneyStage() {
        try {
            const response = await fetch(`${this.baseUrl}/journey/${this.sessionId}`, {
                headers: {
                    'x-api-key': this.apiKey
                }
            });

            const data = await response.json();
            if (!data.success) {
                console.error('Error getting journey stage:', data.error);
            }
            return data;
        } catch (error) {
            console.error('Error getting journey stage:', error);
            return { success: false, error: error.message };
        }
    }

    // Track page view
    trackPageView(pageName, additionalMetadata = {}) {
        const metadata = {
            pageName,
            url: window.location.href,
            referrer: document.referrer,
            ...additionalMetadata
        };
        return this.trackEvent('page_view', metadata);
    }

    // Track product view
    trackProductView(productId, productName, additionalMetadata = {}) {
        const metadata = {
            productId,
            productName,
            ...additionalMetadata
        };
        return this.trackEvent('product_view', metadata);
    }

    // Track add to cart
    trackAddToCart(productId, quantity, price, additionalMetadata = {}) {
        const metadata = {
            productId,
            quantity,
            price,
            ...additionalMetadata
        };
        return this.trackEvent('add_to_cart', metadata);
    }

    // Track purchase
    trackPurchase(orderId, totalAmount, items, additionalMetadata = {}) {
        const metadata = {
            orderId,
            totalAmount,
            items,
            ...additionalMetadata
        };
        return this.trackEvent('purchase', metadata);
    }
}

export default JourneyTracker; 