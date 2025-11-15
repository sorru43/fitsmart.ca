/**
 * Firebase Configuration for FitSmart
 * Initialize Firebase and Analytics
 */

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAT2e7cQ8CV6DI_ekF6CQwxeEa2FBGuRrs",
  authDomain: "fitsmart-web.firebaseapp.com",
  projectId: "fitsmart-web",
  storageBucket: "fitsmart-web.firebasestorage.app",
  messagingSenderId: "233893386700",
  appId: "1:233893386700:web:b65857d303458570996569",
  measurementId: "G-KL81PX3VRR"
};

// Initialize Firebase
let firebaseApp = null;
let analytics = null;

// Initialize Firebase when the SDK is loaded
function initializeFirebase() {
  try {
    // Check if Firebase is loaded
    if (typeof firebase !== 'undefined' && firebase.apps && firebase.apps.length === 0) {
      firebaseApp = firebase.initializeApp(firebaseConfig);
      
      // Initialize Analytics if available
      if (typeof firebase.analytics !== 'undefined') {
        analytics = firebase.analytics();
        console.log('Firebase Analytics initialized');
      }
      
      console.log('Firebase initialized successfully');
      return firebaseApp;
    } else if (typeof firebase !== 'undefined' && firebase.apps && firebase.apps.length > 0) {
      // Firebase already initialized
      firebaseApp = firebase.app();
      console.log('Firebase already initialized');
      return firebaseApp;
    }
  } catch (error) {
    console.error('Error initializing Firebase:', error);
    return null;
  }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeFirebase);
} else {
  initializeFirebase();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { firebaseApp, analytics, firebaseConfig };
}

