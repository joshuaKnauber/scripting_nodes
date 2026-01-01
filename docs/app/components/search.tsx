"use client";
import { create } from "@orama/orama";
import { useDocsSearch } from "fumadocs-core/search/client";
import {
  SearchDialog,
  SearchDialogClose,
  SearchDialogContent,
  SearchDialogHeader,
  SearchDialogIcon,
  SearchDialogInput,
  SearchDialogList,
  SearchDialogOverlay,
  type SharedProps,
} from "fumadocs-ui/components/dialog/search";
import { useI18n } from "fumadocs-ui/contexts/i18n";
import { useMemo } from "react";

function initOrama() {
  return create({
    schema: { _: "string" },
    language: "english",
  });
}

export default function DefaultSearchDialog(props: SharedProps) {
  const { locale } = useI18n();

  // Build the search API path dynamically
  // In production, BASE_URL will be "/scripting_nodes/" so the fetch goes to the correct path
  // In dev, it will be "/" but the static search won't work anyway since routes aren't prerendered
  const searchApiPath = useMemo(() => {
    const base = import.meta.env.BASE_URL ?? "/";
    return `${base}api/search`.replace(/\/+/g, "/");
  }, []);

  const { search, setSearch, query } = useDocsSearch({
    type: "static",
    initOrama,
    from: searchApiPath,
    locale,
  });

  return (
    <SearchDialog
      search={search}
      onSearchChange={setSearch}
      isLoading={query.isLoading}
      {...props}
    >
      <SearchDialogOverlay />
      <SearchDialogContent>
        <SearchDialogHeader>
          <SearchDialogIcon />
          <SearchDialogInput />
          <SearchDialogClose />
        </SearchDialogHeader>
        <SearchDialogList items={query.data !== "empty" ? query.data : null} />
      </SearchDialogContent>
    </SearchDialog>
  );
}
