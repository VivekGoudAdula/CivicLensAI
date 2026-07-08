import type { ButtonProps } from "@/components/ui/button";
import { Button } from "@/components/ui/button";

export function PrimaryButton(props: ButtonProps) {
  return <Button variant="default" {...props} />;
}

export function SecondaryButton(props: ButtonProps) {
  return <Button variant="secondary" {...props} />;
}

export function GhostButton(props: ButtonProps) {
  return <Button variant="ghost" {...props} />;
}

export function IconButton(props: ButtonProps) {
  return <Button variant="ghost" size="icon" {...props} />;
}

export function DangerButton(props: ButtonProps) {
  return <Button variant="destructive" {...props} />;
}

export function LoadingButton({ loading = true, children, ...props }: ButtonProps) {
  return (
    <Button loading={loading} {...props}>
      {children ?? "Loading"}
    </Button>
  );
}
