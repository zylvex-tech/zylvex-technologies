import { AuthProvider } from './store/auth';
import { ToastProvider } from './components/Toast';
import Router from './router';

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router />
      </ToastProvider>
    </AuthProvider>
  );
}
