# Firebase Google Auth + Leaderboard Guide

## Recommendation

Firebase Google Auth is appropriate for the **browser version** if the product needs cloud profiles, cross-device best scores, achievements, or a verified leaderboard. It is not needed for the offline Pygame build. Add it as an optional online layer after the local game loop is stable.

The browser client may contain the Firebase web configuration because those values identify the project rather than grant administrative access. Never ship a Firebase Admin SDK key, service-account JSON, or other server credential in the browser bundle.

## 1. Create and configure Firebase

Create a Firebase project at [Firebase Console](https://console.firebase.google.com/). Enable **Authentication → Sign-in method → Google**, create a Web App, and enable **Cloud Firestore** in production mode. Add the browser app's authorized domain, including the production domain and local development domain.

Install the browser SDK in the web project:

```bash
pnpm add firebase
```

Store the public web configuration in environment variables. These values are safe to expose to the browser, but the project ID must point to the intended Firebase project:

```env
VITE_FIREBASE_API_KEY=your-web-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

## 2. Initialize Firebase and Google sign-in

Create `src/lib/firebase.ts` in the browser project:

```ts
import { getApp, getApps, initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const config = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const app = getApps().length ? getApp() : initializeApp(config);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();

export async function signInWithGoogle() {
  const result = await signInWithPopup(auth, googleProvider);
  return result.user;
}

export async function signOutGoogle() {
  await signOut(auth);
}
```

Use `onAuthStateChanged(auth, callback)` in a React context to keep the UI synchronized. The sign-in button should be optional and should not block offline play.

## 3. Submit a verified score

A browser-only score is not fully trusted because a user can modify JavaScript locally. For a casual prototype, Firestore can store the score directly. For a competitive leaderboard, move score validation to a trusted backend or Firebase Cloud Function and submit a signed run summary instead of accepting arbitrary points.

For the casual version, write the best score per user and mode:

```ts
import { doc, serverTimestamp, setDoc } from "firebase/firestore";
import { db } from "./firebase";

export async function saveBestScore(userId: string, mode: string, score: number, level: number) {
  const scoreRef = doc(db, "scores", `${userId}_${mode}`);
  await setDoc(scoreRef, {
    userId,
    mode,
    score,
    level,
    updatedAt: serverTimestamp(),
  }, { merge: true });
}
```

Before writing, compare against the locally cached best score. Firestore rules should also ensure that a user can write only their own document.

## 4. Read the leaderboard

```ts
import { collection, limit, orderBy, query, getDocs } from "firebase/firestore";
import { db } from "./firebase";

export async function loadLeaderboard(mode: string) {
  const scores = query(
    collection(db, "scores"),
    orderBy("score", "desc"),
    limit(50),
  );
  const snapshot = await getDocs(scores);
  return snapshot.docs
    .map((item) => item.data())
    .filter((item) => item.mode === mode);
}
```

For a larger product, create a separate per-mode collection or a server-maintained leaderboard document. Avoid exposing user email addresses; display a chosen nickname or a shortened anonymous identifier.

## 5. Firestore security rules

These rules allow public leaderboard reads and restrict score writes to the authenticated owner. They do not prevent a malicious authenticated user from claiming an unrealistically high score, so competitive validation still belongs on a trusted backend:

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /scores/{scoreId} {
      allow read: if true;
      allow create, update: if request.auth != null
        && request.resource.data.userId == request.auth.uid
        && request.resource.data.score is number
        && request.resource.data.score >= 0
        && request.resource.data.score <= 100000;
      allow delete: if request.auth != null
        && resource.data.userId == request.auth.uid;
    }
  }
}
```

## Recommended rollout

Keep the current browser version fully playable without sign-in. Add a small **“Save your score online”** prompt after game over. If the user chooses it, open Google sign-in. After authentication succeeds, save the score and show the leaderboard. This preserves fast anonymous play while making the online layer optional and privacy-transparent.
