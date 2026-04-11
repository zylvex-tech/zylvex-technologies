import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialIcons';

import { RootStackParamList } from '../../App';
import { getToken } from '../services/auth';
import { saveSession } from '../services/api';

type SessionStatsScreenNavigationProp = StackNavigationProp<RootStackParamList, 'SessionStats'>;
type SessionStatsScreenRouteProp = RouteProp<RootStackParamList, 'SessionStats'>;

type Props = {
  navigation: SessionStatsScreenNavigationProp;
  route: SessionStatsScreenRouteProp;
};

const SessionStatsScreen: React.FC<Props> = ({ navigation, route }) => {
  const { mindmapId, sessionData } = route.params;
  const { nodeCount, avgFocus, durationSeconds, focusTimeline } = sessionData;

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getFocusQuality = (focus: number) => {
    if (focus > 70) return { label: 'High Focus', color: '#4CAF50', emoji: '🟢' };
    if (focus >= 40) return { label: 'Moderate Focus', color: '#FFC107', emoji: '🟡' };
    return { label: 'Low Focus', color: '#F44336', emoji: '🔴' };
  };

  const handleSaveSession = async () => {
    try {
      const token = await getToken();
      if (token) {
        await saveSession(mindmapId, {
          avg_focus: avgFocus,
          duration_seconds: durationSeconds,
          node_count: nodeCount,
          focus_timeline: focusTimeline,
        });
        Alert.alert('Success', 'Session saved successfully!');
        navigation.navigate('Home');
      }
    } catch (error) {
      console.error('Failed to save session:', error);
      Alert.alert('Error', 'Failed to save session. Please try again.');
    }
  };

  const handleDiscard = () => {
    Alert.alert(
      'Discard Session',
      'Are you sure you want to discard this session?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Discard',
          style: 'destructive',
          onPress: () => navigation.navigate('Home'),
        },
      ]
    );
  };

  const focusQuality = getFocusQuality(avgFocus);

  const renderFocusChart = () => {
    if (focusTimeline.length === 0) {
      return (
        <View style={styles.noDataContainer}>
          <Icon name="show-chart" size={48} color="#ccc" />
          <Text style={styles.noDataText}>No focus data recorded</Text>
        </View>
      );
    }

    const maxFocus = Math.max(...focusTimeline);
    const minFocus = Math.min(...focusTimeline);

    return (
      <View style={styles.chartContainer}>
        <View style={styles.chartBars}>
          {focusTimeline.slice(0, 10).map((focus, index) => {
            const height = (focus / 100) * 100;
            let color = '#F44336';
            if (focus > 70) color = '#4CAF50';
            else if (focus >= 40) color = '#FFC107';
            
            return (
              <View key={index} style={styles.chartBarContainer}>
                <View style={[styles.chartBar, { height: `${height}%`, backgroundColor: color }]} />
                <Text style={styles.chartLabel}>{index + 1}</Text>
              </View>
            );
          })}
        </View>
        <View style={styles.chartLegend}>
          <Text style={styles.chartStats}>Max: {maxFocus} | Min: {minFocus} | Avg: {avgFocus}</Text>
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
          <Icon name="arrow-back" size={24} color="#4A90E2" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Session Summary</Text>
        <View style={{ width: 40 }} />
      </View>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Session Overview</Text>
        
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{nodeCount}</Text>
            <Text style={styles.statLabel}>Nodes Created</Text>
          </View>
          
          <View style={styles.statItem}>
            <Text style={[styles.statValue, { color: focusQuality.color }]}>
              {avgFocus}
            </Text>
            <Text style={styles.statLabel}>Avg Focus</Text>
          </View>
          
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{formatDuration(durationSeconds)}</Text>
            <Text style={styles.statLabel}>Duration</Text>
          </View>
        </View>

        <View style={styles.focusQuality}>
          <Text style={[styles.focusQualityText, { color: focusQuality.color }]}>
            {focusQuality.emoji} {focusQuality.label}
          </Text>
          <Text style={styles.focusQualityDescription}>
            {avgFocus > 70 ? 'You maintained excellent focus throughout the session!' :
             avgFocus >= 40 ? 'Your focus was moderate. Try to eliminate distractions for better results.' :
             'Your focus was low. Consider taking breaks or changing your environment.'}
          </Text>
        </View>
      </View>

      <View style={styles.chartCard}>
        <Text style={styles.chartTitle}>Focus Level Over Time</Text>
        <Text style={styles.chartSubtitle}>
          Each bar represents focus level at 30-second intervals
        </Text>
        
        {renderFocusChart()}
        
        <View style={styles.chartLegend}>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#4CAF50' }]} />
            <Text style={styles.legendText}>High Focus (>70)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#FFC107' }]} />
            <Text style={styles.legendText}>Moderate (40-70)</Text>
          </View>
          <View style={styles.legendItem}>
            <View style={[styles.legendColor, { backgroundColor: '#F44336' }]} />
            <Text style={styles.legendText}>Low Focus (<40)</Text>
          </View>
        </View>
      </View>

      <View style={styles.insightsCard}>
        <Text style={styles.insightsTitle}>Insights & Recommendations</Text>
        
        <View style={styles.insightItem}>
          <Icon name="lightbulb" size={20} color="#4A90E2" />
          <Text style={styles.insightText}>
            {nodeCount > 10 ? 'Great productivity! You expanded your mind map significantly.' :
             'Consider adding more nodes to develop your ideas further.'}
          </Text>
        </View>
        
        <View style={styles.insightItem}>
          <Icon name="trending-up" size={20} color="#4A90E2" />
          <Text style={styles.insightText}>
            {avgFocus > 70 ? 'Your high focus suggests an optimal working environment.' :
             'Try using the focus simulator to track and improve your concentration.'}
          </Text>
        </View>
        
        <View style={styles.insightItem}>
          <Icon name="schedule" size={20} color="#4A90E2" />
          <Text style={styles.insightText}>
            {durationSeconds > 300 ? 'Good session length! Deep work requires extended focus.' :
             'Try longer sessions to develop more complex thought structures.'}
          </Text>
        </View>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.actionButton, styles.discardButton]}
          onPress={handleDiscard}
        >
          <Icon name="delete" size={20} color="#F44336" />
          <Text style={styles.discardButtonText}>Discard Session</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.saveButton]}
          onPress={handleSaveSession}
        >
          <Icon name="save" size={20} color="#fff" />
          <Text style={styles.saveButtonText}>Save Session</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Saved sessions help track your focus patterns over time and improve productivity.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 15,
    paddingVertical: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: { padding: 5 },
  headerTitle: { fontSize: 20, fontWeight: '600', color: '#333' },
  summaryCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  summaryTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, color: '#333' },
  statsGrid: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  statItem: { alignItems: 'center', flex: 1 },
  statValue: { fontSize: 28, fontWeight: 'bold', color: '#4A90E2', marginBottom: 5 },
  statLabel: { fontSize: 14, color: '#666' },
  focusQuality: { backgroundColor: '#f8f9fa', padding: 15, borderRadius: 8 },
  focusQualityText: { fontSize: 16, fontWeight: 'bold', marginBottom: 5 },
  focusQualityDescription: { fontSize: 14, color: '#666', lineHeight: 20 },
  chartCard: {
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginBottom: 15,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  chartTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 5, color: '#333' },
  chartSubtitle: { fontSize: 14, color: '#666', marginBottom: 15 },
  chartContainer: { alignItems: 'center', marginVertical: 15 },
  chartBars: { flexDirection: 'row', alignItems: 'flex-end', height: 150, marginBottom: 10 },
  chartBarContainer: { alignItems: 'center', marginHorizontal: 4, flex: 1 },
  chartBar: { width: 20, borderRadius: 4, backgroundColor: '#4A90E2' },
  chartLabel: { fontSize: 10, color: '#666', marginTop: 5 },
  chartStats: { fontSize: 12, color: '#666', marginTop: 10 },
  noDataContainer: { alignItems: 'center', justifyContent: 'center', height: 150 },
  noDataText: { fontSize: 16, color: '#999', marginTop: 10 },
  chartLegend: { flexDirection: 'row', justifyContent: 'space-around', marginTop: 15 },
  legendItem: { flexDirection: 'row', alignItems: 'center' },
  legendColor: { width: 12, height: 12, borderRadius: 6, marginRight: 5 },
  legendText: { fontSize: 12, color: '#666' },
  insightsCard: {
    backgroundColor: '#fff',
    marginHorizontal: 15,
    marginBottom: 15,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  insightsTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, color: '#333' },
  insightItem: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 12 },
  insightText: { flex: 1, fontSize: 14, color: '#555', marginLeft: 10, lineHeight: 20 },
  actions: { flexDirection: 'row', justifyContent: 'space-between', marginHorizontal: 15, marginBottom: 15 },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    flex: 1,
    marginHorizontal: 5,
  },
  discardButton: { backgroundColor: '#fff', borderWidth: 1, borderColor: '#F44336' },
  saveButton: { backgroundColor: '#4A90E2' },
  discardButtonText: { color: '#F44336', fontWeight: '600', marginLeft: 8 },
  saveButtonText: { color: '#fff', fontWeight: '600', marginLeft: 8 },
  footer: { padding: 15, alignItems: 'center' },
  footerText: { fontSize: 12, color: '#999', textAlign: 'center', fontStyle: 'italic' },
});

export default SessionStatsScreen;
