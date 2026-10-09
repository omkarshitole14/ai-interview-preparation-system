import type { CandidateProfile as CandidateProfileType } from "@/types/resume";

type CandidateProfileProps = {
  profile: CandidateProfileType;
};

export default function CandidateProfile({
  profile,
}: CandidateProfileProps) {
  return (
    <div className="space-y-6">
      <ProfileSection title="Skills">
        <div className="flex flex-wrap gap-2">
          {profile.skills.length > 0 ? (
            profile.skills.map((skill, index) => (
              <span
                key={index}
                className="rounded-full border border-blue-100 bg-blue-50 px-3 py-1.5 text-sm text-blue-700"
              >
                {skill}
              </span>
            ))
          ) : (
            <p className="text-sm text-slate-400">
              No information detected.
            </p>
          )}
        </div>
      </ProfileSection>

      <ProfileList
        title="Education"
        items={profile.education}
      />

      <ProfileList
        title="Projects"
        items={profile.projects}
      />

      <ProfileList
        title="Experience"
        items={profile.experience}
      />

      <ProfileList
        title="Certifications"
        items={profile.certifications}
      />
    </div>
  );
}

function ProfileSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="mb-4 font-semibold">{title}</h3>
      {children}
    </div>
  );
}

function ProfileList({
  title,
  items,
}: {
  title: string;
  items: string[];
}) {
  return (
    <ProfileSection title={title}>
      {items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item, index) => (
            <div
              key={index}
              className="rounded-lg border border-slate-100 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-700"
            >
              {item}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-slate-400">
          No information detected.
        </p>
      )}
    </ProfileSection>
  );
}