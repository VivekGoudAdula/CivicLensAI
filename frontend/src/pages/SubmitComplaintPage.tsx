import { useMemo, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { ImageUpload, type ImageUploadValue } from "@/components/complaints/image-upload";
import { LocationPicker, type LocationValue } from "@/components/complaints/location-picker";
import { VoiceRecorder, type VoiceRecordingValue } from "@/components/complaints/voice-recorder";
import { showErrorToast, showSuccessToast } from "@/components/feedback/toast";
import { PageHeader } from "@/components/layout/PageHeader";
import { SkeletonForm } from "@/components/loading/skeleton-form";
import { PrimaryButton } from "@/components/ui/buttons";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Textarea } from "@/components/ui/textarea";
import type { Category } from "@/types/complaint";
import { useCategories } from "@/hooks/use-categories";
import { useCreateComplaint } from "@/hooks/use-complaints";
import { ApiError } from "@/lib/api-client";

const complaintFormSchema = z
  .object({
    title: z
      .string()
      .min(5, "Title must be at least 5 characters")
      .max(256, "Title must be at most 256 characters"),
    description: z
      .string()
      .min(10, "Description must be at least 10 characters")
      .max(5000, "Description must be at most 5000 characters"),
    category_id: z.string().min(1, "Please select a category"),
    address: z
      .string()
      .min(3, "Address is required")
      .max(500, "Address must be at most 500 characters"),
    landmark: z.string().max(256, "Landmark must be at most 256 characters").optional(),
    contact_name: z.string().max(128).optional(),
    mobile_number: z
      .string()
      .regex(/^[6-9]\d{9}$/, "Enter a valid 10-digit Indian mobile number"),
    is_anonymous: z.boolean(),
  })
  .superRefine((data, ctx) => {
    if (!data.is_anonymous && !data.contact_name?.trim()) {
      ctx.addIssue({
        code: "custom",
        message: "Contact name is required when not submitting anonymously",
        path: ["contact_name"],
      });
    }
  });

type ComplaintFormValues = z.infer<typeof complaintFormSchema>;

export function SubmitComplaintPage() {
  const navigate = useNavigate();
  const { data: categoriesData, isLoading: categoriesLoading } = useCategories();
  const createMutation = useCreateComplaint();

  const [location, setLocation] = useState<LocationValue | null>(null);
  const [image, setImage] = useState<ImageUploadValue | null>(null);
  const [audio, setAudio] = useState<VoiceRecordingValue | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<ComplaintFormValues>({
    resolver: zodResolver(complaintFormSchema),
    defaultValues: {
      title: "",
      description: "",
      category_id: "",
      address: "",
      landmark: "",
      contact_name: "",
      mobile_number: "",
      is_anonymous: false,
    },
  });

  const isAnonymous = watch("is_anonymous");
  const categories = useMemo(() => categoriesData?.items ?? [], [categoriesData]);

  const onSubmit = handleSubmit(async (values) => {
    if (!location) {
      setLocationError("Please select a location on the map");
      return;
    }
    setLocationError(null);

    try {
      const response = await createMutation.mutateAsync({
        title: values.title,
        description: values.description,
        category_id: values.category_id,
        latitude: location.latitude,
        longitude: location.longitude,
        address: values.address || location.address,
        landmark: values.landmark || undefined,
        contact_name: values.is_anonymous ? undefined : values.contact_name,
        mobile_number: values.mobile_number,
        is_anonymous: values.is_anonymous,
        image: image
          ? {
              data: image.data,
              mime_type: image.mime_type,
              file_name: image.file_name,
            }
          : undefined,
        audio: audio
          ? {
              data: audio.data,
              mime_type: audio.mime_type,
            }
          : undefined,
        audio_duration_seconds: audio?.duration_seconds,
      });

      showSuccessToast("Complaint submitted", response.message);
      navigate(`/complaints/success?id=${response.complaint.id}`);
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : "Failed to submit complaint";
      showErrorToast("Submission failed", message);
    }
  });

  if (categoriesLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <PageHeader title="Submit Complaint" description="Loading form..." />
        <SkeletonForm fields={8} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <PageHeader
        title="Submit Complaint"
        description="Report a civic issue in your constituency. All fields marked with context are validated before submission."
      />

      <form onSubmit={onSubmit} className="space-y-6" noValidate>
        <Card>
          <CardHeader>
            <CardTitle>Complaint Details</CardTitle>
            <CardDescription>Describe the issue clearly for faster resolution.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Complaint Title *</Label>
              <Input id="title" placeholder="e.g. Broken road near main market" {...register("title")} />
              {errors.title ? (
                <p className="text-sm text-destructive">{errors.title.message}</p>
              ) : null}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Complaint Description *</Label>
              <Textarea
                id="description"
                rows={5}
                placeholder="Provide details about the issue, when it started, and its impact..."
                {...register("description")}
              />
              {errors.description ? (
                <p className="text-sm text-destructive">{errors.description.message}</p>
              ) : null}
            </div>

            <div className="space-y-2">
              <Label>Category *</Label>
              <Select
                value={watch("category_id")}
                onValueChange={(value) => setValue("category_id", value, { shouldValidate: true })}
              >
                <SelectTrigger aria-label="Select complaint category">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category: Category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.category_id ? (
                <p className="text-sm text-destructive">{errors.category_id.message}</p>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Location</CardTitle>
            <CardDescription>Pin the exact location of the issue on the map.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <LocationPicker
              value={location}
              onChange={(next) => {
                setLocation(next);
                setLocationError(null);
                setValue("address", next.address, { shouldValidate: true });
              }}
              error={locationError ?? undefined}
            />

            <div className="space-y-2">
              <Label htmlFor="address">Address *</Label>
              <Input
                id="address"
                placeholder="Address will auto-fill from map"
                {...register("address")}
              />
              {errors.address ? (
                <p className="text-sm text-destructive">{errors.address.message}</p>
              ) : null}
            </div>

            <div className="space-y-2">
              <Label htmlFor="landmark">Landmark</Label>
              <Input id="landmark" placeholder="Nearby landmark (optional)" {...register("landmark")} />
              {errors.landmark ? (
                <p className="text-sm text-destructive">{errors.landmark.message}</p>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Attachments</CardTitle>
            <CardDescription>Add a photo or voice note to support your complaint.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <ImageUpload value={image} onChange={setImage} />
            <VoiceRecorder value={audio} onChange={setAudio} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
            <CardDescription>
              Your contact details help officials follow up. Enable anonymous mode to hide your name.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">Submit Anonymously</p>
                <p className="text-sm text-muted-foreground">
                  Your name will not be shown publicly
                </p>
              </div>
              <Switch
                checked={isAnonymous}
                onCheckedChange={(checked) => setValue("is_anonymous", checked)}
                aria-label="Submit anonymously"
              />
            </div>

            {!isAnonymous ? (
              <div className="space-y-2">
                <Label htmlFor="contact_name">Contact Name *</Label>
                <Input id="contact_name" placeholder="Your full name" {...register("contact_name")} />
                {errors.contact_name ? (
                  <p className="text-sm text-destructive">{errors.contact_name.message}</p>
                ) : null}
              </div>
            ) : null}

            <div className="space-y-2">
              <Label htmlFor="mobile_number">Mobile Number *</Label>
              <Input
                id="mobile_number"
                type="tel"
                inputMode="numeric"
                placeholder="10-digit mobile number"
                maxLength={10}
                {...register("mobile_number")}
              />
              {errors.mobile_number ? (
                <p className="text-sm text-destructive">{errors.mobile_number.message}</p>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-3">
          <PrimaryButton
            type="submit"
            loading={isSubmitting || createMutation.isPending}
            disabled={isSubmitting || createMutation.isPending}
          >
            Submit Complaint
          </PrimaryButton>
        </div>
      </form>
    </div>
  );
}
