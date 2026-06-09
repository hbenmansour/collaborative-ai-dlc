'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { configureAmplify, getUser, getUserRoles, signOut } from '@/lib/auth';
import { Hub } from 'aws-amplify/utils';

interface AuthUser {
  userId: string;
  username: string;
  roles: string[];
}

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  handleSignOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  handleSignOut: async () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    configureAmplify();
    checkUser();

    const unsubscribe = Hub.listen('auth', ({ payload }) => {
      if (payload.event === 'signedIn') checkUser();
      if (payload.event === 'signedOut') setUser(null);
    });

    return () => unsubscribe();
  }, []);

  async function checkUser() {
    try {
      const cognitoUser = await getUser();
      if (cognitoUser) {
        const roles = await getUserRoles();
        setUser({
          userId: cognitoUser.userId,
          username: cognitoUser.username,
          roles,
        });
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function handleSignOut() {
    await signOut();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, handleSignOut }}>
      {children}
    </AuthContext.Provider>
  );
}
