// Centralized API utility for stackgnosis frontend
import {toast} from "./shared/components/Toast";
import getCSRFToken from "./utils";

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem("accessToken");
  return token ? { Authorization: `Token ${token}` } : {};
}


export const api = {
  /**
  * Register a new user
  */
  async registerUser(formData: any): Promise<any> {
    // Now retrieve the CSRF token
    const csrfToken = getCSRFToken();
    const response = await fetch('/api/users/register/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
          ...getAuthHeaders()
        },
        body: JSON.stringify(formData),
        credentials: 'include',
      });
    return response;
  },
    
  /**
   * Login a user and store accessTokens in sessionStorage
   */
  async loginUser(formData: any): Promise<any> {
    const response = await fetch('/api/users/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData),
    });
    return response;
  },
  /**
   * Get User
   */
  async getUser(slug: string): Promise<any> {
    const response = await fetch(`/api/users/me/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      credentials: 'include',
    });
    return response;
  },

  /**
   * Fetch all entries
   */
  async getEntries(query?: string): Promise<any[]> {
    const url = query && query.trim()
    ? `/api/entries/?q=${encodeURIComponent(query.trim())}`
    : '/api/entries/';
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      credentials: 'include',
    });
    if (!response.ok) throw new Error('Failed to fetch entries');
    // Some components use JSON.parse(data), so support both string and object
    const data = await response.json();
    try {
      return typeof data === 'string' ? JSON.parse(data) : data;
    } catch {
      return data;
    }
  },

  /**
   * Fetch a single entry by slug
   */
  async getEntry(slug: string): Promise<any> {
    const response = await fetch(`/api/entries/${slug}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      credentials: 'include',
    });
    if (response.status === 404) {
      throw new Error('Entry not found');
    }
    if (!response.ok) throw new Error('Failed to fetch entry');
    const data = await response.json();    
    if (data && data.results && Array.isArray(data.results)) {
      return data.results[0];
    }
    return data;
  },
  /**
   * Search entries
   */
  async searchEntries(query: string): Promise<any> {
    const response = await fetch(`/api/entries/search/?q=${query}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      credentials: 'include',
    });
    if (!response.ok) throw new Error('Failed to search entries');
    const data = await response.json();
    return data;
  },
  /**
   * Create a new entry
   * Sent from CreateEntry component
   */
  async createEntry(entryData: any): Promise<any> {
    const response = await fetch('/api/entries/create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify(entryData),
      credentials: 'include',
    });
    return response;
  },

  /**
   * Request a new entry
   * Does not return response. User will receive notification when request is fulfilled.
   */
  requestNewEntry(entryData: string) {
    fetch('/api/entries/request-new/', {
      method: 'POST',
      body: JSON.stringify({'query': entryData}),
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders() 
      },
      credentials: 'include',
    });
    toast.info(`New entry for ${entryData} requested.`);
  },
  /**
   * Delete an entry
   */
  async deleteEntry(slug: string): Promise<any> {
    const response = await fetch(`/api/entries/${slug}/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      credentials: 'include',
    });
    return response;
  },
  /**
   * View Bookmarks
   * 
   */
  async getBookmarks(slug: string): Promise<any[]> {
    const response = await fetch(`/api/users/${slug}/bookmarks/`, {
      method: 'GET',
      headers: { ...getAuthHeaders() },
      credentials: 'include',
    });
    if (!response.ok) throw new Error('Failed to fetch bookmarks');
    const data = await response.json();
    try {
      return typeof data === 'string' ? JSON.parse(data) : data;
    } catch {
      return data;
    }
  },
  async testNotification(slug: string) {
    const response = await fetch(`/api/notify/${slug}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      credentials: 'include',
    });
    if (!response.ok) throw new Error('Failed to test notification');
    const data = await response.json();
    return data;
  },
  
};
