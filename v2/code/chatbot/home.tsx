// Importam axios pentru cereri HTTP
import axios from 'axios';
// Importam React si hook-ul useState
import React, { useState } from 'react';
// Importam componentele UI din React Native
import { Button, KeyboardAvoidingView, Platform, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

export default function HomeScreen() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);

  const sendQuestion = async () => {
    if (!question.trim()) return;

    const newMessages = [...messages, { sender: 'You', text: question }];
    setMessages(newMessages);
    setQuestion('');

    try {
      const res = await axios.post<{ response: string }>(
        'http://wifi_ip_address:5050/chat',
        { question }
      );
      setMessages([...newMessages, { sender: 'Bot', text: res.data.response }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { sender: 'Bot', text: 'Eroare la conectare cu serverul Flask.' },
      ]);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={-50} // adjust this if needed
      >
        <View style={styles.container}>
          <ScrollView
            style={styles.chatBox}
            contentContainerStyle={{ paddingBottom: 20 }}
          >
            {messages.map((msg, index) => (
              <Text
                key={index}
                style={msg.sender === 'You' ? styles.userMsg : styles.botMsg}
              >
                {msg.sender}: {msg.text}
              </Text>
            ))}
          </ScrollView>

          <View style={styles.inputRow}>
            <TextInput
              style={styles.input}
              value={question}
              onChangeText={setQuestion}
              placeholder="Intreaba ceva..."
            />
            <Button title="Trimite" onPress={sendQuestion} />
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, paddingTop: 50 },
  chatBox: { flex: 1, marginBottom: 10 },
  userMsg: {
    alignSelf: 'flex-end',
    backgroundColor: '#cce',
    margin: 5,
    padding: 8,
    borderRadius: 5,
  },
  botMsg: {
    alignSelf: 'flex-start',
    backgroundColor: '#eee',
    margin: 5,
    padding: 8,
    borderRadius: 5,
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Platform.OS === 'ios' ? 40 : 0, // give it a little lift on iOS
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 10,
    marginRight: 10,
    borderRadius: 5,
  },
});