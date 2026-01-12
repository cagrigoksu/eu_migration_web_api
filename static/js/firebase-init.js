
if (!firebase.apps || firebase.apps.length === 0) {
    if (typeof firebaseConfig !== 'undefined') {
        firebase.initializeApp(firebaseConfig);
    }
}