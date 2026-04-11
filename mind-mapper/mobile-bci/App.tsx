import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import HomeScreen from './src/screens/HomeScreen';
import MindMapEditorScreen from './src/screens/MindMapEditorScreen';
import SessionStatsScreen from './src/screens/SessionStatsScreen';

export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Home: undefined;
  MindMapEditor: { mindmapId: string; title: string };
  SessionStats: { mindmapId: string; sessionData: any };
};

const Stack = createStackNavigator<RootStackParamList>();

const App = () => {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Login">
          <Stack.Screen 
            name="Login" 
            component={LoginScreen} 
            options={{ title: 'Mind Mapper Login' }}
          />
          <Stack.Screen 
            name="Register" 
            component={RegisterScreen} 
            options={{ title: 'Create Account' }}
          />
          <Stack.Screen 
            name="Home" 
            component={HomeScreen} 
            options={{ title: 'My Mind Maps' }}
          />
          <Stack.Screen 
            name="MindMapEditor" 
            component={MindMapEditorScreen} 
            options={({ route }) => ({ title: route.params.title || 'Mind Map' })}
          />
          <Stack.Screen 
            name="SessionStats" 
            component={SessionStatsScreen} 
            options={{ title: 'Session Summary' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
};

export default App;
