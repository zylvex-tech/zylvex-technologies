import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import * as Location from 'expo-location';
import { apiService, authService } from '../services/auth';

const NearbyScreen = ({ navigation }) => {
  const [location, setLocation] = useState(null);
  const [anchors, setAnchors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userAnchors, setUserAnchors] = useState([]);

  useEffect(() => {
    checkAuthentication();
    requestLocationPermission();
  }, []);

  useEffect(() => {
    if (location) {
      fetchNearbyAnchors();
      if (isAuthenticated) {
        fetchUserAnchors();
      }
    }
  }, [location, isAuthenticated]);

  const checkAuthentication = async () => {
    const authenticated = await authService.isAuthenticated();
    setIsAuthenticated(authenticated);
  };

  const requestLocationPermission = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Permission to access location was denied');
      setLoading(false);
      return;
    }

    const currentLocation = await Location.getCurrentPositionAsync({});
    setLocation(currentLocation);
  };

  const fetchNearbyAnchors = async () => {
    try {
      setLoading(true);
      const result = await apiService.getNearbyAnchors(
        location.coords.latitude,
        location.coords.longitude,
        1.0 // 1km radius
      );
      setAnchors(result.anchors || []);
    } catch (error) {
      Alert.alert('Error', `Failed to fetch anchors: ${error.message}`);
      console.error('Fetch anchors error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserAnchors = async () => {
    try {
      if (isAuthenticated) {
        const result = await apiService.getMyAnchors();
        setUserAnchors(result || []);
      }
    } catch (error) {
      console.error('Fetch user anchors error:', error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchNearbyAnchors();
    if (isAuthenticated) {
      await fetchUserAnchors();
    }
    setRefreshing(false);
  };

  const handleDeleteAnchor = async (anchorId) => {
    Alert.alert(
      'Delete Anchor',
      'Are you sure you want to delete this anchor?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await apiService.deleteAnchor(anchorId);
              Alert.alert('Success', 'Anchor deleted successfully');
              // Refresh lists
              fetchNearbyAnchors();
              fetchUserAnchors();
            } catch (error) {
              Alert.alert('Error', `Failed to delete anchor: ${error.message}`);
            }
          },
        },
      ]
    );
  };

  const renderAnchorItem = ({ item }) => (
    <View style={styles.anchorItem}>
      <View style={styles.anchorContent}>
        <Text style={styles.anchorTitle}>{item.title || 'Untitled Anchor'}</Text>
        <Text style={styles.anchorDescription}>
          {item.content || 'No description'}
        </Text>
        <Text style={styles.anchorLocation}>
          Location: {item.latitude.toFixed(6)}, {item.longitude.toFixed(6)}
        </Text>
        <Text style={styles.anchorType}>Type: {item.content_type}</Text>
        <Text style={styles.anchorDate}>
          Created: {new Date(item.created_at).toLocaleDateString()}
        </Text>
        {item.owner_name && (
          <Text style={styles.anchorOwner}>Owner: {item.owner_name}</Text>
        )}
      </View>
      
      {isAuthenticated && userAnchors.some(a => a.id === item.id) && (
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => handleDeleteAnchor(item.id)}
        >
          <Text style={styles.deleteButtonText}>Delete</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#4a6fa5" />
        <Text style={styles.loadingText}>Loading anchors...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Nearby Anchors</Text>
        <Text style={styles.headerSubtitle}>
          {location 
            ? `Your location: ${location.coords.latitude.toFixed(6)}, ${location.coords.longitude.toFixed(6)}`
            : 'Location unavailable'}
        </Text>
        
        {!isAuthenticated && (
          <TouchableOpacity
            style={styles.authButton}
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.authButtonText}>Login to manage your anchors</Text>
          </TouchableOpacity>
        )}
        
        {isAuthenticated && userAnchors.length > 0 && (
          <View style={styles.userAnchorsInfo}>
            <Text style={styles.userAnchorsText}>
              You have {userAnchors.length} anchor(s) in this area
            </Text>
          </View>
        )}
      </View>

      <FlatList
        data={anchors}
        renderItem={renderAnchorItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={handleRefresh}
            colors={['#4a6fa5']}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>No anchors found nearby</Text>
            <Text style={styles.emptySubtext}>
              Create your first anchor using the Camera tab!
            </Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4a6fa5',
    marginBottom: 5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  authButton: {
    backgroundColor: '#4a6fa5',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  authButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  userAnchorsInfo: {
    backgroundColor: '#e8f4fd',
    padding: 10,
    borderRadius: 8,
    marginTop: 10,
    borderWidth: 1,
    borderColor: '#b3d9ff',
  },
  userAnchorsText: {
    color: '#0066cc',
    fontSize: 14,
  },
  list: {
    padding: 10,
  },
  anchorItem: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  anchorContent: {
    flex: 1,
  },
  anchorTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  anchorDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  anchorLocation: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  anchorType: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  anchorDate: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  anchorOwner: {
    fontSize: 12,
    color: '#4a6fa5',
    fontWeight: '600',
    marginTop: 5,
  },
  deleteButton: {
    backgroundColor: '#ff6b6b',
    padding: 8,
    borderRadius: 6,
    alignItems: 'center',
    marginTop: 10,
  },
  deleteButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emptyContainer: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
  },
});

export default NearbyScreen;
