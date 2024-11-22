import * as React from "react";
import { View, Text } from "react-native";
import { styled } from "nativewind/styled";

const StyledView = styled(View);
const StyledText = styled(Text);

const Card = ({ children, className = "" }) => {
  return (
    <StyledView className={`bg-white rounded-lg shadow-sm p-4 ${className}`}>
      {children}
    </StyledView>
  );
};

const CardHeader = ({ children, className = "" }) => {
  return (
    <StyledView className={`space-y-1.5 p-2 ${className}`}>
      {children}
    </StyledView>
  );
};

const CardTitle = ({ children, className = "" }) => {
  return (
    <StyledText className={`text-lg font-semibold text-text ${className}`}>
      {children}
    </StyledText>
  );
};

const CardContent = ({ children, className = "" }) => {
  return (
    <StyledView className={`p-2 pt-0 ${className}`}>
      {children}
    </StyledView>
  );
};

export { Card, CardHeader, CardTitle, CardContent };
