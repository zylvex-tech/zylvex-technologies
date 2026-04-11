import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useNavigation } from '@react-navigation/native';
import { anchorAPI } from '../services/api';
import { requestCameraPermission, requestLocationPermission, getCurrentLocation } from '../utils/permissions';

const CameraScreen = () => {
  const navigation = useNavigation();
  const cameraRef = useRef(null);
  
  const [permission, requestPermission] = useCameraPermissions();
  const [isLoading, setIsLoading] = useState(false);
  const [showInputModal, setShowInputModal] = useState(false);
  const [anchorContent, setAnchorContent] = useState('');
  
  useEffect(() => {
    const checkPermissions = async () => {
      try {
        const cameraResult = await requestCameraPermission();
        if (!cameraResult.granted) {
          Alert.alert('Camera Permission Required', 'Camera access is needed to place AR anchors');
        }
        
        const locationResult = await requestLocationPermission();
        if (!locationResult.granted) {
          Alert.alert('Location Permission Required', 'Location access is needed to save anchor positions');
        }
      } catch (error) {
        console.error('Error checking permissions:', error);
      }
    };
    
    checkPermissions();
  }, []);
  
  const handleCameraTap = async (event) => {
    if (isLoading) return;
    setShowInputModal(true);
  };
  
  const handleCreateAnchor = async () => {
    if (!anchorContent.trim()) {
      Alert.alert('Error', 'Please enter some content for the anchor');
      return;
    }
    
    setIsLoading(true);
    
    try {
      const location = await getCurrentLocation();
      
      const anchorData = {
        user_id: 'demo_user',
        content_type: 'text',
        content_data: JSON.stringify({ text: anchorContent }),
        title: `Anchor: ${anchorContent.substring(0, 20)}${anchorContent.length > 20 ? '...' : ''}`,
        description: `Placed at ${new Date().toLocaleString()}`,
        latitude: location.latitude,
        longitude: location.longitude,
        altitude: location.altitude || 0,
      };
      
      await anchorAPI.createAnchor(anchorData);
      
      Alert.alert(
        'Success',
        'Anchor placed successfully!',
        [
          { text: 'OK', onPress: () => {
            setAnchorContent('');
            setShowInputModal(false);
            setIsLoading(false);
          }},
          { 
            text: 'View Nearby', 
            onPress: () => {
              setAnchorContent('');
              setShowInputModal(false);
              setIsLoading(false);
              navigation.navigate('Nearby');
            }
          },
        ]
      );
      
    } catch (error) {
      console.error('Error creating anchor:', error);
      Alert.alert('Error', 'Failed to place anchor. Please try again.');
      setIsLoading(false);
    }
  };
  
  const navigateToNearby = () => {
    navigation.navigate('Nearby');
  };
  
  const renderCamera = () => {
    if (!permission?.granted) {
      return (
        <View style={styles.permissionContainer}>
          <Text style={styles.permissionText}>Camera permission is required</Text>
          <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
            <Text style={styles.permissionButtonText}>Grant Permission</Text>
          </TouchableOpacity>
        </View>
      );
    }
    
    return (
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing="back"
        onTouchEnd={handleCameraTap}
      >
        <View style={styles.overlay}>
          <View style={styles.crosshair} />
          <Text style={styles.instructionText}>Tap anywhere to place an anchor</Text>
        </View>
      </CameraView>
    );
  };
  
  return (
    <View style={styles.container}>
      {renderCamera()}
      
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.navButton} onPress={navigateToNearby}>
          <Text style={styles.navButtonText}>View Nearby Anchors</Text>
        </TouchableOpacity>
        
        <Text style={styles.hintText}>Point camera at a surface and tap to place anchor</Text>
      </View>
      
      <Modal
        visible={showInputModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowInputModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Create Anchor</Text>
            <Text style={styles.modalSubtitle}>Enter text or emoji for your anchor</Text>
            
            <TextInput
              style={styles.input}
              placeholder="Enter text or emoji..."
              value={anchorContent}
              onChangeText={setAnchorContent}
              autoFocus={true}
              maxLength={100}
            />
            
            <View style={styles.modalButtons}>
              <TouchableOpacity 
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => {
                  setShowInputModal(false);
                  setAnchorContent('');
                }}
                disabled={isLoading}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.modalButton, styles.submitButton]}
                onPress={handleCreateAnchor}
                disabled={isLoading}
              >
                {isLoading ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text style={styles.submitButtonText}>Place Anchor</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  camera: { flex: 1 },
  overlay: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  crosshair: { width: 40, height: 40, borderWidth: 2, borderColor: 'rgba(255, 255, 255, 0.7)', borderRadius: 20 },
  instructionText: { position: 'absolute', bottom: 100, color: 'white', fontSize: 16, backgroundColor: 'rgba(0, 0, 0, 0.5)', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 20 },
  permissionContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f5f5f5', padding: 20 },
  permissionText: { fontSize: 18, marginBottom: 20, textAlign: 'center' },
  permissionButton: { backgroundColor: '#007AFF', paddingHorizontal: 30, paddingVertical: 15, borderRadius: 10 },
  permissionButtonText: { color: 'white', fontSize: 16, fontWeight: 'bold' },
  bottomBar: { backgroundColor: 'rgba(0, 0, 0, 0.8)', padding: 15, alignItems: 'center' },
  navButton: { backgroundColor: '#007AFF', paddingHorizontal: 30, paddingVertical: 12, borderRadius: 25, marginBottom: 10 },
  navButtonText: { color: 'white', fontSize: 16, fontWeight: 'bold' },
  hintText: { color: 'rgba(255, 255, 255, 0.7)', fontSize: 14, textAlign: 'center' },
  modalOverlay: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: 'rgba(0, 0, 0, 0.5)' },
  modalContent: { backgroundColor: 'white', borderRadius: 20, padding: 25, width: '85%', maxWidth: 400 },
  modalTitle: { fontSize: 22, fontWeight: 'bold', marginBottom: 5 },
  modalSubtitle: { fontSize: 14, color: '#666', marginBottom: 20 },
  input: { borderWidth: 1, borderColor: '#ddd', borderRadius: 10, padding: 15, fontSize: 16, marginBottom: 20 },
  modalButtons: { flexDirection: 'row', justifyContent: 'space-between' },
  modalButton: { flex: 1, paddingVertical: 15, borderRadius: 10, alignItems: 'center', marginHorizontal: 5 },
  cancelButton: { backgroundColor: '#f0f0f0' },
  submitButton: { backgroundColor: '#007AFF' },
  cancelButtonText: { color: '#333', fontSize: 16, fontWeight: '600' },
  submitButtonText: { color: 'white', fontSize: 16, fontWeight: '600' },
});

export default CameraScreen;
