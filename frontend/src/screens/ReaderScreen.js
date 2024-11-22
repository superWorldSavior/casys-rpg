import React from 'react';
import { View, Text, ScrollView } from 'react-native';
import { styled } from "nativewind/styled";

const StyledView = styled(View);
const StyledText = styled(Text);

export default function ReaderScreen() {
  return (
    <StyledView className="flex-1 bg-background">
      <ScrollView className="flex-1 p-4">
        <StyledView className="mb-6">
          <StyledText className="text-xl font-bold text-text mb-4">
            Story Content
          </StyledText>
          <StyledText className="text-gray-600 leading-6">
            Your story content will appear here with mobile-optimized formatting...
          </StyledText>
        </StyledView>
      </ScrollView>
    </StyledView>
  );
}
