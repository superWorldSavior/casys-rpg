import React from 'react';
import { View, Text, Switch, ScrollView } from 'react-native';
import { styled } from "nativewind/styled";

const StyledView = styled(View);
const StyledText = styled(Text);

export default function SettingsScreen() {
  const [isDarkMode, setIsDarkMode] = React.useState(false);

  return (
    <StyledView className="flex-1 bg-background">
      <ScrollView className="flex-1 p-4">
        <StyledView className="mb-6">
          <StyledText className="text-xl font-bold text-text mb-4">
            Reader Settings
          </StyledText>
          
          <StyledView className="flex-row justify-between items-center p-4 bg-white rounded-lg">
            <StyledText className="text-text">Dark Mode</StyledText>
            <Switch
              value={isDarkMode}
              onValueChange={setIsDarkMode}
            />
          </StyledView>
        </StyledView>
      </ScrollView>
    </StyledView>
  );
}
