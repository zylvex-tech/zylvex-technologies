import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal, TextInput, Alert, ScrollView, ActivityIndicator } from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import Slider from '@react-native-community/slider';

import { RootStackParamList } from '../../App';
import { getToken } from '../services/auth';
import { createNode, deleteNode, getMindMapNodes } from '../services/api';

type MindMapEditorScreenNavigationProp = StackNavigationProp<RootStackParamList, 'MindMapEditor'>;
type MindMapEditorScreenRouteProp = RouteProp<RootStackParamList, 'MindMapEditor'>;

type Props = {
  navigation: MindMapEditorScreenNavigationProp;
  route: MindMapEditorScreenRouteProp;
};

type Node = {
  id: string;
  text: string;
  parent_id: string | null;
  color: string;
  font_size: number;
  focus_level: number;
};

const MindMapEditorScreen: React.FC<Props> = ({ navigation, route }) => {
  const { mindmapId, title } = route.params;
  const [nodes, setNodes] = useState<Node[]>([]);
  const [focusLevel, setFocusLevel] = useState(70);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newNodeText, setNewNodeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [sessionStartTime] = useState(Date.now());
  const [focusTimeline, setFocusTimeline] = useState<number[]>([70]);

  // Load existing nodes on mount
  useEffect(() => {
    const loadNodes = async () => {
      try {
        const existingNodes = await getMindMapNodes(mindmapId);
        if (existingNodes && existingNodes.length > 0) {
          setNodes(existingNodes.map((n: any) => ({
            id: String(n.id),
            text: n.text,
            parent_id: n.parent_id ? String(n.parent_id) : null,
            color: n.color || '#4A90E2',
            font_size: getNodeFontSize(n.focus_level),
            focus_level: n.focus_level,
          })));
          setSelectedNodeId(String(existingNodes[0].id));
        } else {
          // New mind map — seed a root node placeholder (UI only, not persisted)
          setNodes([{ id: 'root', text: title, parent_id: null, color: '#4A90E2', font_size: 20, focus_level: 70 }]);
          setSelectedNodeId('root');
        }
      } catch (error) {
        console.error('Failed to load nodes:', error);
        setNodes([{ id: 'root', text: title, parent_id: null, color: '#4A90E2', font_size: 20, focus_level: 70 }]);
        setSelectedNodeId('root');
      } finally {
        setInitializing(false);
      }
    };
    loadNodes();
  }, [mindmapId]);

  useEffect(() => {
    const interval = setInterval(() => {
      setFocusTimeline(prev => [...prev, focusLevel]);
    }, 30000);
    return () => clearInterval(interval);
  }, [focusLevel]);

  const getFocusLabel = (level: number) => {
    if (level > 70) return 'High Focus 🟢';
    if (level >= 40) return 'Moderate 🟡';
    return 'Low Focus 🔴';
  };

  const getNodeColor = (level: number) => {
    if (level > 70) return '#4CAF50';
    if (level >= 40) return '#FFC107';
    return '#F44336';
  };

  const getNodeFontSize = (level: number) => {
    if (level > 70) return 18;
    if (level >= 40) return 16;
    return 14;
  };

  const handleAddNode = async () => {
    if (!selectedNodeId || !newNodeText.trim()) {
      Alert.alert('Error', 'Please select a node and enter text');
      return;
    }

    setLoading(true);
    try {
      const newNode: Node = {
        id: `node_${Date.now()}`,
        text: newNodeText.trim(),
        parent_id: selectedNodeId,
        color: getNodeColor(focusLevel),
        font_size: getNodeFontSize(focusLevel),
        focus_level: focusLevel,
      };

      const token = await getToken();
      if (token) {
        await createNode(mindmapId, {
          text: newNode.text,
          parent_id: newNode.parent_id,
          focus_level: newNode.focus_level,
          color: newNode.color,
          x: 0,
          y: 0,
        });
      }

      setNodes(prev => [...prev, newNode]);
      setNewNodeText('');
      setShowAddModal(false);
    } catch (error) {
      console.error('Failed to add node:', error);
      Alert.alert('Error', 'Failed to add node. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteNode = async (nodeId: string) => {
    if (nodeId === 'root') {
      Alert.alert('Error', 'Cannot delete the root node');
      return;
    }

    Alert.alert(
      'Delete Node',
      'Are you sure you want to delete this node?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const token = await getToken();
              if (token) {
                await deleteNode(mindmapId, nodeId);
              }
              setNodes(prev => prev.filter(node => node.id !== nodeId));
            } catch (error) {
              console.error('Failed to delete node:', error);
              Alert.alert('Error', 'Failed to delete node. Please try again.');
            }
          },
        },
      ]
    );
  };

  const handleNodePress = (nodeId: string) => {
    setSelectedNodeId(nodeId);
  };

  const handleNodeLongPress = (nodeId: string) => {
    handleDeleteNode(nodeId);
  };

  const handleFocusChange = (value: number) => {
    setFocusLevel(Math.round(value));
  };

  const handleSaveAndExit = () => {
    const sessionDuration = Math.round((Date.now() - sessionStartTime) / 1000);
    const avgFocus = focusTimeline.length > 0 
      ? Math.round(focusTimeline.reduce((a, b) => a + b, 0) / focusTimeline.length)
      : focusLevel;
    
    navigation.navigate('SessionStats', {
      mindmapId,
      sessionData: {
        nodeCount: nodes.length,
        avgFocus,
        durationSeconds: sessionDuration,
        focusTimeline,
      },
    });
  };

  const renderNode = (node: Node) => (
    <TouchableOpacity
      key={node.id}
      style={[
        styles.node,
        { backgroundColor: node.id === selectedNodeId ? '#e3f2fd' : '#fff', borderColor: node.color },
      ]}
      onPress={() => handleNodePress(node.id)}
      onLongPress={() => handleNodeLongPress(node.id)}
    >
      <Text style={[styles.nodeText, { fontSize: node.font_size, color: '#333' }]}>
        {node.text.length > 20 ? node.text.substring(0, 20) + '...' : node.text}
      </Text>
      {node.parent_id && (
        <Text style={styles.nodeFocus}>Focus: {node.focus_level}</Text>
      )}
    </TouchableOpacity>
  );

  if (initializing) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#4A90E2" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={handleSaveAndExit}>
          <Icon name="arrow-back" size={24} color="#4A90E2" />
          <Text style={styles.backButtonText}>Save & Exit</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>{title}</Text>
        <TouchableOpacity
          style={styles.addButton}
          onPress={() => setShowAddModal(true)}
          disabled={!selectedNodeId}
        >
          <Icon name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.nodesContainer}>
        {nodes.map(renderNode)}
      </ScrollView>

      <View style={styles.focusPanel}>
        <Text style={styles.focusLabel}>{getFocusLabel(focusLevel)}</Text>
        <View style={styles.sliderContainer}>
          <Text style={styles.focusValue}>0</Text>
          <Slider
            style={styles.slider}
            minimumValue={0}
            maximumValue={100}
            value={focusLevel}
            onValueChange={handleFocusChange}
            minimumTrackTintColor={getNodeColor(focusLevel)}
            maximumTrackTintColor="#e0e0e0"
            thumbTintColor={getNodeColor(focusLevel)}
          />
          <Text style={styles.focusValue}>100</Text>
        </View>
        <Text style={styles.focusLevelText}>Current: {focusLevel}</Text>
        <Text style={styles.focusHint}>
          {focusLevel > 70 ? 'High focus creates green nodes with larger text' :
           focusLevel >= 40 ? 'Moderate focus creates yellow nodes with normal text' :
           'Low focus creates red nodes with smaller text'}
        </Text>
      </View>

      <Modal visible={showAddModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Add Child Node</Text>
            <Text style={styles.modalSubtitle}>
              Adding to: {nodes.find(n => n.id === selectedNodeId)?.text || 'None'}
            </Text>
            
            <TextInput
              style={styles.modalInput}
              placeholder="Enter node text"
              value={newNodeText}
              onChangeText={setNewNodeText}
              autoFocus
              maxLength={50}
            />
            
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={[styles.modalButton, styles.cancelButton]}
                onPress={() => {
                  setShowAddModal(false);
                  setNewNodeText('');
                }}
                disabled={loading}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={[styles.modalButton, styles.addButtonModal, !newNodeText.trim() && styles.disabledButton]}
                onPress={handleAddNode}
                disabled={loading || !newNodeText.trim()}
              >
                {loading ? (
                  <ActivityIndicator color="#fff" size="small" />
                ) : (
                  <Text style={styles.addButtonText}>Add Node</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      <View style={styles.instructions}>
        <Text style={styles.instructionsText}>
          • Tap a node to select it • Long press to delete • Adjust focus slider to affect new nodes
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 10,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: { flexDirection: 'row', alignItems: 'center', padding: 5 },
  backButtonText: { color: '#4A90E2', fontSize: 16, marginLeft: 5 },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    flex: 1,
    textAlign: 'center',
    marginHorizontal: 10,
  },
  addButton: {
    backgroundColor: '#4A90E2',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  nodesContainer: { flex: 1, padding: 15 },
  node: {
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#4A90E2',
  },
  nodeText: { fontWeight: '500' },
  nodeFocus: { fontSize: 12, color: '#666', marginTop: 5 },
  focusPanel: {
    backgroundColor: '#fff',
    padding: 15,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  focusLabel: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  slider: { flex: 1, height: 40 },
  focusValue: { fontSize: 14, color: '#666', width: 30, textAlign: 'center' },
  focusLevelText: { fontSize: 16, textAlign: 'center', marginBottom: 5 },
  focusHint: { fontSize: 14, color: '#666', textAlign: 'center', fontStyle: 'italic' },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    width: '80%',
  },
  modalTitle: { fontSize: 20, fontWeight: 'bold', marginBottom: 5 },
  modalSubtitle: { fontSize: 14, color: '#666', marginBottom: 15 },
  modalInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    fontSize: 16,
    marginBottom: 20,
  },
  modalButtons: { flexDirection: 'row', justifyContent: 'space-between' },
  modalButton: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 5,
    minWidth: 100,
    alignItems: 'center',
  },
  cancelButton: { backgroundColor: '#f5f5f5' },
  cancelButtonText: { color: '#666' },
  addButtonModal: { backgroundColor: '#4A90E2' },
  disabledButton: { backgroundColor: '#ccc' },
  addButtonText: { color: '#fff', fontWeight: 'bold' },
  instructions: {
    backgroundColor: '#fff',
    padding: 10,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  instructionsText: { fontSize: 12, color: '#666', textAlign: 'center' },
});

export default MindMapEditorScreen;
