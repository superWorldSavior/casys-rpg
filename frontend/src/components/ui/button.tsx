import * as React from "react";
import { Pressable, Text } from "react-native";
import { styled } from "nativewind/styled";
import { cva, type VariantProps } from "class-variance-authority";

const buttonVariants = cva(
  "flex-row items-center justify-center rounded-md",
  {
    variants: {
      variant: {
        default: "bg-primary",
        destructive: "bg-red-500",
        outline: "border border-input bg-background",
        secondary: "bg-secondary",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

const StyledPressable = styled(Pressable);
const StyledText = styled(Text);

interface ButtonProps extends VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
  onPress?: () => void;
  disabled?: boolean;
}

const Button = ({ 
  children, 
  variant = "default", 
  size = "default", 
  onPress,
  disabled = false,
}: ButtonProps) => {
  return (
    <StyledPressable
      className={buttonVariants({ variant, size })}
      onPress={onPress}
      disabled={disabled}
    >
      <StyledText 
        className={`text-sm font-medium ${
          variant === "default" || variant === "destructive" 
            ? "text-white" 
            : "text-text"
        }`}
      >
        {children}
      </StyledText>
    </StyledPressable>
  );
};

export { Button, buttonVariants };
