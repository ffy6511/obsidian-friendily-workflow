import React from "react";
import { COLORS } from "../theme/colors";
import { FONTS } from "../theme/typography";
import { BRAND } from "../timeline";

interface TopBarProps {
  /** Every section of the cut, "xx | yy". The active one is set in the
   *  primary text colour, the rest stay secondary. */
  sections?: string[];
  active?: string;
}

/** Persistent top chrome for the middle scenes: brand on the left, the
 *  chapter strip in the middle, a fixed line on the right. */
export const TopBar: React.FC<TopBarProps> = ({ sections, active }) => {
  return (
    <header
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 80,
        padding: "0 56px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        background: COLORS.bg,
        borderBottom: `1px solid ${COLORS.cardBorder}`,
        zIndex: 50,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 12, width: 280 }}>
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: 8,
            background: COLORS.primary,
            color: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: FONTS.title,
            fontWeight: 700,
            fontSize: 20,
          }}
        >
          {BRAND.name.slice(0, 1)}
        </div>
        <span
          style={{
            fontFamily: FONTS.title,
            fontWeight: 600,
            fontSize: 26,
            letterSpacing: 2,
            color: COLORS.textPrimary,
          }}
        >
          {BRAND.name}
        </span>
      </div>

      {sections ? (
        <nav style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {sections.map((section, i) => {
            const isActive = section === active;
            return (
              <React.Fragment key={section}>
                {i > 0 ? (
                  <span
                    style={{
                      fontFamily: FONTS.body,
                      fontSize: 17,
                      fontWeight: 500,
                      color: COLORS.textMuted,
                      opacity: 0.55,
                    }}
                  >
                    |
                  </span>
                ) : null}
                <span
                  style={{
                    fontFamily: FONTS.body,
                    fontSize: 19,
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? COLORS.textPrimary : COLORS.textMuted,
                    letterSpacing: 0.2,
                    whiteSpace: "nowrap",
                  }}
                >
                  {section}
                </span>
              </React.Fragment>
            );
          })}
        </nav>
      ) : null}

      <div
        style={{
          width: 280,
          textAlign: "right",
          fontFamily: FONTS.mono,
          fontSize: 15,
          color: COLORS.textSecondary,
        }}
      >
        {BRAND.repoLine}
      </div>
    </header>
  );
};
