import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  Button,
  Image,
  ActivityIndicator,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform
} from 'react-native';

const API_URL = Platform.select({
  ios: 'http://localhost:8000/api/v1/suggest-sticker',
  android: 'http://10.0.2.2:8000/api/v1/suggest-sticker',
  default: 'http://localhost:8000/api/v1/suggest-sticker'
});

export default function App() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [imageBase64, setImageBase64] = useState(null);
  const [emotion, setEmotion] = useState(null);
  const [suggestions, setSuggestions] = useState([]);

  const handleGenerateSticker = async () => {
    if (!text.trim()) {
      Alert.alert('Error', 'Por favor ingresa un texto');
      return;
    }

    setLoading(true);
    setImageBase64(null);
    setEmotion(null);
    setSuggestions([]);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();

      if (data.generated_image_base64) {
        setImageBase64(data.generated_image_base64);
      } else {
        Alert.alert('Advertencia', 'No se generó imagen en la respuesta');
      }

      setEmotion(data.detected_emotion || 'N/A');
      setSuggestions(Array.isArray(data.suggestions) ? data.suggestions : []);
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.card}>
          <Text style={styles.title}>Sticker AI</Text>
          <Text style={styles.label}>Escribe un texto para generar tu sticker</Text>
          <TextInput
            style={styles.input}
            multiline
            placeholder="Ingresa tu mensaje..."
            value={text}
            onChangeText={setText}
            editable={!loading}
          />
          <View style={styles.buttonContainer}>
            <Button
              title={loading ? 'Generando...' : 'Generar sticker'}
              onPress={handleGenerateSticker}
              disabled={loading}
            />
          </View>

          {loading && <ActivityIndicator size="large" color="#2b6cb0" style={styles.loader} />}

          {emotion && (
            <View style={styles.resultHeader}>
              <Text style={styles.resultTitle}>Emoción detectada</Text>
              <Text style={styles.emotionText}>{emotion}</Text>
            </View>
          )}

          {suggestions.length > 0 && (
            <View style={styles.suggestionsContainer}>
              <Text style={styles.resultTitle}>Sugerencias</Text>
              {suggestions.map((item) => (
                <View key={item.id} style={styles.suggestionItem}>
                  <Text style={styles.suggestionName}>{item.name}</Text>
                  <Text style={styles.suggestionDescription}>{item.description}</Text>
                </View>
              ))}
            </View>
          )}

          {imageBase64 ? (
            <Image
              style={styles.resultImage}
              source={{ uri: `data:image/png;base64,${imageBase64}` }}
              resizeMode="contain"
            />
          ) : (
            !loading && (
              <View style={styles.placeholderContainer}>
                <Text style={styles.placeholderText}>Aquí se mostrará tu sticker generado</Text>
              </View>
            )
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc'
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 24
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 6 },
    elevation: 4
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    marginBottom: 12,
    color: '#1e293b'
  },
  label: {
    fontSize: 16,
    color: '#475569',
    marginBottom: 12
  },
  input: {
    minHeight: 100,
    borderColor: '#cbd5e1',
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    fontSize: 16,
    color: '#0f172a',
    backgroundColor: '#f8fafc',
    textAlignVertical: 'top'
  },
  buttonContainer: {
    marginTop: 16,
    marginBottom: 20
  },
  loader: {
    marginVertical: 20
  },
  resultHeader: {
    marginBottom: 12
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 6
  },
  emotionText: {
    fontSize: 16,
    color: '#0f766e'
  },
  suggestionsContainer: {
    marginBottom: 20
  },
  suggestionItem: {
    marginBottom: 10,
    padding: 12,
    backgroundColor: '#e2e8f0',
    borderRadius: 10
  },
  suggestionName: {
    fontWeight: '700',
    color: '#1e293b'
  },
  suggestionDescription: {
    color: '#475569',
    marginTop: 2
  },
  resultImage: {
    width: '100%',
    height: 280,
    borderRadius: 16,
    backgroundColor: '#e2e8f0'
  },
  placeholderContainer: {
    height: 280,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f8fafc'
  },
  placeholderText: {
    color: '#94a3b8',
    textAlign: 'center',
    paddingHorizontal: 10
  }
});
