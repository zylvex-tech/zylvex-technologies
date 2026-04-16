import { AuthProvider } from './store/auth';
import { NotificationsProvider } from './store/notifications';
import { ToastProvider } from './components/Toast';
import Router from './router';

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <NotificationsProvider>
          <Router />
        </NotificationsProvider>
      </ToastProvider>
    </AuthProvider>
  );
}
