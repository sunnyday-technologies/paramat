# ParaMat — Print Conditions

Search or scan a 3D-printing filament and get **brand-specific** consensus print
conditions (nozzle/bed temperatures as ranges, flow, density), with a
strength/finish goal toggle and provenance. Static, open, no server. Optional
export writes **OpenSpool 1.0 JSON/NDEF** to compatible **NTAG215/216** tags
through Chrome/Android Web NFC. ParaMat does not currently emit OpenPrintTag or
OpenTag3D records.

**Live:** https://paramat3d.com/

Conditions are a statistical cross-source consensus of open data. They are
decision-support starting points, not measured optima; single-source materials
are flagged. See NOTICE for data attribution.

Tag-format references:

- [OpenSpool](https://github.com/spuder/OpenSpool)
- [OpenPrintTag](https://specs.openprinttag.org/) — separate NFC-V/ISO 15693
  CBOR/NDEF path, not currently emitted
- [OpenTag3D](https://opentag3d.info/spec.html) — separate binary NDEF format,
  not currently emitted

## License

Code: [MIT](LICENSE) · Data: [CC BY 4.0](DATA_LICENSE.md) · Upstream attribution: [NOTICE.md](NOTICE.md)
