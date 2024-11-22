import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/contexts/AuthContext';
import Logo from '@/components/Logo';

export const Login = () => {
  const { isAuthenticated, login, error } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/library');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <Logo size={80} />
      <h1 className="text-3xl font-bold mt-6 mb-8">TextFlow Navigator</h1>
      <div className="w-full max-w-sm space-y-4">
        <div className="w-full max-w-md mx-auto">
          <GoogleLogin
            onSuccess={login}
            onError={() => {
              console.error('Login Failed');
            }}
            useOneTap
            type="standard"
            theme="filled_blue"
            shape="rectangular"
            size="large"
            text="continue_with"
          />
        </div>
        {error && (
          <div className="text-destructive text-sm text-center bg-destructive/10 p-2 rounded">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};
