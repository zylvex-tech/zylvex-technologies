import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Swipeable from 'react-native-gesture-handler/Swipeable';
import { RectButton } from 'react-native-gesture-handler';

import { RootStackParamList } from '../../App';
import { getMindMaps, deleteMindMap } from '../services/api';
import { getToken, clearToken } from '../services/auth';
import { API_BASE_URL } from '../config';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;
type HomeScreenRouteProp = RouteProp<RootStackParamList, 'Home'>;

type Props = {
  navigation: HomeScreenNavigationProp;
  route: HomeScreenRouteProp;
};

type MindMap = {
  id: string;
  title: string;
  node_count: number;
  updated_at: string;
  created_at: string;
};

const HomeScreen: React.FC<Props> = ({ navigation }) => {
  const [mindMaps, setMindMaps] = useState<MindMap[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchMindMaps = useCallback(async () => {
    try {
      const token = await getToken();
      if (!token) {
        navigation.replace('Login');
        return;
      }

      const data = await getMindMaps();
      setMindMaps(data);
    } catch (error) {
      console.error('Failed to fetch mind maps:', error);
      Alert.alert('Error', 'Failed to load mind maps. Please try again.');
      
      // If unauthorized, redirect to login
      if ((error as any).response?.status === 401) {
        await clearToken();
        navigation.replace('Login');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [navigation]);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', fetchMindMaps);
    return unsubscribe;
  }, [navigation, fetchMindMaps]);

  useEffect(() => {
    fetchMindMaps();
  }, [fetchMindMaps]);

  const handleCreateMindMap = () => {
    Alert.prompt(
      'New Mind Map',
      'Enter a title for your new mind map:',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Create',
          onPress: async (title) => {
            if (!title || title.trim() === '') {
              Alert.alert('Error', 'Please enter a title');
              return;
            }

            try {
              const response = await fetch(`${API_BASE_URL}/api/v1/mindmaps`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${await getToken()}`,
                },
                body: JSON.stringify({ title: title.trim() }),
              });

              if (response.ok) {
                const newMindMap = await response.json();
                navigation.navigate('MindMapEditor', {
                  mindmapId: newMindMap.id,
                  title: newMindMap.title,
                });
              } else {
                throw new Error('Failed to create mind map');
              }
            } catch (error) {
              console.error('Failed to create mind map:', error);
              Alert.alert('Error', 'Failed to create mind map. Please try again.');
            }
          },
        },
      ],
      'plain-text',
      '',
      'My New Mind Map'
    );
  };

  const handleDeleteMindMap = async (id: string, title: string) => {
    Alert.alert(
      'Delete Mind Map',
      `Are you sure you want to delete "${title}"? This action cannot be undone.`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteMindMap(id);
              setMindMaps(prev => prev.filter(mindMap => mindMap.id !== id));
            } catch (error) {
              console.error('Failed to delete mind map:', error);
              Alert.alert('Error', 'Failed to delete mind map. Please try again.');
            }
          },
        },
      ]
    );
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            await clearToken();
            navigation.replace('Login');
          },
        },
      ]
    );
  };

  const renderRightActions = (mindMap: MindMap) => {
    return (
      <RectButton
        style={styles.deleteAction}
        onPress={() => handleDeleteMindMap(mindMap.id, mindMap.title)}
      >
        <Icon name="delete" size={24} color="#fff" />
        <Text style={styles.deleteActionText}>Delete</Text>
      </RectButton>
    );
  };

  const renderMindMapItem = ({ item }: { item: MindMap }) => {
    const formatDate = (dateString: string) => {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
      <Swipeable renderRightActions={() => renderRightActions(item)}>
        <TouchableOpacity
          style={styles.mindMapItem}
          onPress={() => {
            navigation.navigate('MindMapEditor', {
              mindmapId: item.id,
              title: item.title,
            });
          }}
        >
          <View style={styles.mindMapContent}>
            <Text style={styles.mindMapTitle}>{item.title}</Text>
            <View style={styles.mindMapMeta}>
              <Text style={styles.mindMapNodes}>{item.node_count} nodes</Text>
              <Text style={styles.mindMapDate}>Updated: {formatDate(item.updated_at)}</Text>
            </View>
          </View>
          <Icon name="chevron-right" size={24} color="#666" />
        </TouchableOpacity>
      </Swipeable>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#4A90E2" />
        <Text style={styles.loadingText}>Loading your mind maps...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Mind Maps</Text>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Icon name="logout" size={24} color="#4A90E2" />
        </TouchableOpacity>
      </View>

      <FlatList
        data={mindMaps}
        renderItem={renderMindMapItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => {
              setRefreshing(true);
              fetchMindMaps();
            }}
            colors={['#4A90E2']}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Icon name="psychology" size={64} color="#ccc" />
            <Text style={styles.emptyText}>No mind maps yet</Text>
            <Text style={styles.emptySubtext}>Create your first mind map to get started</Text>
          </View>
        }
      />

      <TouchableOpacity
        style={styles.createButton}
        onPress={handleCreateMindMap}
      >
        <Icon name="add" size={30} color="#fff" />
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  logoutButton: {
    padding: 5,
  },
  listContent: {
    padding: 10,
  },
  mindMapItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  mindMapContent: {
    flex: 1,
  },
  mindMapTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 5,
  },
  mindMapMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  mindMapNodes: {
    fontSize: 14,
    color: '#666',
  },
  mindMapDate: {
    fontSize: 12,
    color: '#999',
  },
  deleteAction: {
    backgroundColor: '#ff3b30',
    justifyContent: 'center',
    alignItems: 'center',
    width: 80,
    height: '80%',
    borderRadius: 10,
    marginLeft: 10,
  },
  deleteActionText: {
    color: '#fff',
    fontSize: 12,
    marginTop: 5,
  },
  createButton: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#4A90E2',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 5,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  emptyContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
  },
  emptyText: {
    fontSize: 18,
    color: '#999',
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#ccc',
    textAlign: 'center',
    paddingHorizontal: 40,
  },
});

export default HomeScreen;
