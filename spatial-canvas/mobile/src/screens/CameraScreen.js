// CameraScreen.js - Minimal version for commit
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const CameraScreen = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Camera Screen</Text>
      <Text style={styles.subtext}>AR camera for placing anchors</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
  text: {
    color: 'white',
    fontSize: 24,
    fontWeight: 'bold',
  },
  subtext: {
    color: '#ccc',
    fontSize: 16,
    marginTop: 10,
  },
});

export default CameraScreen;
