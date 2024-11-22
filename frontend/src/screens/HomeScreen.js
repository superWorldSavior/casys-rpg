import React from 'react';
import { View, ScrollView } from 'react-native';
import { styled } from "nativewind/styled";
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

const StyledView = styled(View);

export default function HomeScreen({ navigation }) {
  return (
    <StyledView className="flex-1 bg-background">
      <ScrollView className="flex-1 p-4">
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Welcome to Solo RPG AI Narrator</CardTitle>
          </CardHeader>
          <CardContent>
            <Button
              variant="default"
              size="lg"
              onPress={() => navigation.navigate('Reader')}
              className="mb-4 w-full"
            >
              Start Reading
            </Button>
            
            <Button
              variant="secondary"
              size="lg"
              onPress={() => navigation.navigate('Settings')}
              className="w-full"
            >
              Settings
            </Button>
          </CardContent>
        </Card>
      </ScrollView>
    </StyledView>
  );
}
