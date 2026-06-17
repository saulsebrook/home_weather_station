const ATC_DATA = [
  // ── CLASS C ──
  {
    classes: ['C'], type: 'clearance', title: 'IFR Clearance — Class C',
    note: 'Request clearance from Delivery before start. Read back all items.',
    format: '[ATC Delivery], [Callsign], [Aircraft Type], [MEDEVAC if applicable], for [Destination], request clearance',
    examples: [
      { label: 'RSCU533 MEDEVAC', text: 'Brisbane Delivery, RSCU533, helicopter, MEDEVAC, for YXHE, request clearance' },
      { label: 'ATC response', text: 'RSCU533, cleared to YXHE via amended BLHS, YXHE, climb to A025, squawk 1256, departure frequency 124.7' },
    ]
  },
  {
    classes: ['C'], type: 'clearance', title: 'VFR Clearance — Class C',
    note: 'Request VFR departure clearance from Delivery specifying altitude and destination.',
    format: '[ATC Delivery], [Callsign] [Aircraft Type], request VFR departure to [Destination] at [Altitude]',
    examples: [
      { label: 'Pilot', text: 'Brisbane Delivery, FD412 Kingair 350, request VFR departure to Toowoomba at 8,500' },
    ]
  },
  {
    classes: ['C'], type: 'taxi', title: 'Circuits — Class C',
    note: 'Clearance to conduct circuits.',
    format: 'ATC Unit, Callsign, for circuits, request clearance',
    examples: [
      { label: 'Pilot', text: 'Melbourne Delivery, LKU, for circuits, request clearance' },
      { label: 'ATC response', text: 'LKU, cleared to operate in the circuit area, not above A020, squawk 0100' },
      { label: 'Pilot', text: 'Cleared to operate in the circuit area, not above A020, squawk 0100, LKU' },
    ]
  },
  {
    classes: ['C'], type: 'circuits', title: 'Taxi — Class C',
    note: 'Report bay/pad number. Cite ATIS after callsign. Read back full taxi instructions. Request Ground/Air taxi, or Air transit.',
    format: '[ATC Ground], [Callsign], [Location], [ATIS], request taxi',
    examples: [
      { label: 'Pilot', text: 'Brisbane Ground, FD412, GA ramp, request taxi for VFR departure with Lima' },
      { label: 'Helicopter — air taxi', text: 'Bankstown Ground, HSZ, taxiway F, for the main pad, received V, request air taxi' },
      { label: 'ATC response', text: 'HSZ, air taxi to the main pad' },
    ]
  },
   {
    classes: ['D'], type: 'circuits', title: 'Taxi — Class D',
    note: 'Report bay/pad number. Cite ATIS after callsign. Read back full taxi instructions. Request Ground/Air taxi, or Air transit.',
    format: '[ATC Ground], [Callsign], [Location], [ATIS], request taxi',
    examples: [
      { label: 'Pilot', text: 'Brisbane Ground, FD412, GA ramp, request taxi for VFR departure with Lima' },
      { label: 'Helicopter — air taxi', text: 'Bankstown Ground, HSZ, taxiway F, for the main pad, received V, request air taxi' },
      { label: 'ATC response', text: 'HSZ, air taxi to the main pad' },
    ]
  },
  {
    classes: ['C'], type: 'departure', title: 'Ready for lineup — Class C',
    note: 'Contact tower when ready at holding point. After takeoff contact Departures.',
    format: '[ATC Tower], [Callsign], ready',
    examples: [
      { label: 'Pilot ready', text: 'Brisbane Tower, RSCU533, Taxiway H2, ready' },
      { label: 'ATC clearance', text: 'RSCU533, Brisbane Tower, Taxiway H2 cleared for takeoff' },
    ]
  },
  {
    classes: ['C'], type: 'departure', title: 'Outside Manouvering area — Class C',
    note: 'Helicopters and some light aircraft may operate from areas outside the manoeuvring area, such as hospital helipads or small airstrips inside the CTR, or other locations on the aerodrome. A takeoff/landing clearance will not be provided in these situations but approval must be sought to become airborne inside the control zone. After obtaining an airways clearance, ATC will instruct you to 'report airborne' or 'report on the ground'.',
    format: '[ATC Tower], [Type][Callsign], [Location], for [Destination], received [ATIS], ready',
    examples: [
      { label: 'Pilot ready', text: 'Sydney Tower, helicopter RSCU201, St George Hospital, for YSBK, received F, ready' },
      { label: 'ATC clearance', text: 'RSCU201, cleared to YSBK direct, climb to A015 visual, squawk 0466, report airborne' },
      { label: 'Pilot', text: 'Cleared to YSBK direct, climb to A015 visual, squawk 0466, RSCU201' },
      { label: 'Pilot', text: 'RSCU201, airborne' },
    ]
  },
  {
    classes: ['C'], type: 'inbound', title: 'Inbound — Class C (Helicopter)',
    note: 'Helicopters inbound to YSSY use named inbound routes. Report position on route.',
    format: '[ATC Tower], helicopter [Callsign], [Position/Route], [Level], inbound [Helipad], received [ATIS]',
    examples: [
      { label: 'YOE inbound YSSY via Maroubra route', text: 'Sydney Tower, helicopter YOE' },
      { label: 'ATC response', text: 'YOE, Sydney Tower, cleared visual approach to H8, report on the ground' },
      { label: 'On pad', text: 'YOE on the pad' },
    ]
  },
  {
    classes: ['C'], type: 'inbound', title: 'Inbound — First contact approach',
    note: 'Making first contact with approach enroute',
    format: 'ATC Unit, Callsign, Cleared Level, [Visual], received ATIS Code',
    examples: [
      { label: 'QFA on descent to A090 approaching YSSY', text: 'Sydney Approach, QFA426, descending to A090, received Delta' },
    ]
  },
  {
    classes: ['C'], type: 'inbound', title: 'Inbound — Entering Class C from uncontrolled',
    note: 'Contact Approach with position, track, level and ATIS before entering Class C.',
    format: '[Approach], [Callsign], [Distance] miles [Direction] tracking [Reporting Point], inbound, with [ATIS]',
    examples: [
      { label: 'Careflight inbound Sydney', text: 'Sydney Approach, Careflight 21, X miles N tracking the R405 Harbour Bridge, inbound, with Alpha' },
    ]
  },
  {
    classes: ['C'], type: 'approach', title: 'Approach — ILS in CTA',
    note: 'Request instrument approach in CTA. ATC will vector you to intercept.',
    format: '[Callsign] request the [Approach type] approach runway [RWY] to the minima',
    examples: [
      { label: 'Pilot request', text: 'UNF request the YSRI ILS approach runway 28 to the minima' },
      { label: 'ATC vectors', text: 'UNF, turn right heading 360, expect ILS approach runway 28' },
      { label: 'Cleared', text: 'UNF, turn left heading 310 to intercept the localiser, cleared ILS approach runway 28, report in the missed approach' },
    ]
  },
  {
    classes: ['C'], type: 'airwork', title: 'Airwork — Clearance in CTA',
    note: 'Clearance required before conducting airwork within CTA.',
    format: '[Callsign] request airwork within a [Distance]nm radius of [Position] between [Level] and [Level] for the next [Time] minutes',
    examples: [
      { label: 'Pilot request', text: 'OIT request airwork within a 5nm radius of PEGSU between A080 and A100 for the next 15 minutes' },
      { label: 'ATC cleared', text: 'OIT, cleared to operate within a 5nm radius of PEGSU, A080 to A100' },
      { label: 'Read back', text: 'Cleared to operate within a 5nm radius of PEGSU, A080 to A100, OIT' },
    ]
  },
  {
    classes: ['C'], type: 'general', title: 'VFR Corridor Clearance',
    note: 'Request corridor clearance from Tower. Clearance limit and lateral constraints will be issued.',
    format: '[ATC Tower], [Callsign], [Entry Point], [Level], for the [Corridor Name], request clearance',
    examples: [
      { label: 'Cairns Western Corridor', text: 'Cairns Tower, NDR, EDT, A015, for the Western VFR Corridor, request clearance' },
      { label: 'ATC clearance', text: 'NDR, enter the CTR tracking via the Western VFR Corridor at A015. Clearance limit is ADI, remain on or west of the Western VFR Corridor at all times' },
    ]
  },
  {
    classes: ['C'], type: 'inbound', title: 'VFR Inbound — Class C',
    note: 'Request clearance from Tower with position, level and ATIS.',
    format: '[ATC Tower], [Callsign], [Position], [Level], inbound, [ATIS], request clearance',
    examples: [
      { label: 'Cairns inbound', text: 'Cairns Tower, NDR, Cape Grafton, A005, inbound, information Alpha, request clearance' },
      { label: 'ATC', text: 'NDR, enter the CTR tracking for a right base runway 33, A005' },
    ]
  },

  // ── CLASS D ──
  {
    classes: ['D'], type: 'inbound', title: 'Inbound — Class D',
    note: 'Standard inbound call includes distance, aerodrome name, track/radial, level, and ATIS.',
    format: '[ATC Unit], [Callsign], [Distance] miles [Aerodrome] on the [Track/Radial], descending to [Level], [visual], ATIS [Code]',
    examples: [
      { label: 'Fixed wing inbound YCFS', text: 'YCFS Tower, RXA6416, 32 miles Coffs Harbour on the 189 radial, descending to A080, visual, received Oscar' },
      { label: 'Moorabbin inbound', text: 'Moorabbin Tower, EWZ, C172, CARR, A015, inbound, in receipt of P' },
      { label: 'ATC join instruction', text: 'EWZ, Moorabbin Tower, join downwind runway 17R' },
      { label: 'Read back', text: 'Join downwind runway 17R, EWZ' },
    ]
  },
  {
    classes: ['D'], type: 'taxi', title: 'Taxi — Class D',
    note: 'Cite bay number, received ATIS, and departure direction.',
    format: '[ATC Ground], [Callsign], [Aircraft Type], [Location], for [departure direction], received [ATIS], request taxi',
    examples: [
      { label: 'Archer Ground', text: 'Archer Ground, Archer BHK, Dual, received F, at Eastern Apron, for southern departure, request taxi' },
      { label: 'ATC', text: 'BHK, Archer Ground, report approaching taxiway E' },
      { label: 'Taxi instruction', text: 'BHK, taxi E, B, cross runway 04R, 04L, holding point B6, runway 10L' },
      { label: 'Moorabbin upwind dep', text: 'Moorabbin Ground, VCY, Cessna 152, Southern Runup Bay, for an upwind departure, received Uniform, request taxi' },
    ]
  },
  {
    classes: ['D'], type: 'departure', title: 'Departure — Delta Transition',
    note: 'Northbound/southbound transitions through Class D require clearance from Tower.',
    format: '[ATC Tower], [Callsign], [Level], [Location], [Direction] transition',
    examples: [
      { label: 'Delta transition', text: 'Archerfield Tower, CHR21, 3000ft, [location], northbound transition' },
    ]
  },
  {
    classes: ['D'], type: 'inbound', title: 'VFR Inbound — Class D (Moorabbin)',
    note: 'Include reporting point, altitude and ATIS.',
    format: '[Aerodrome] [ATC Unit], [Callsign], approaching [Point] [Altitude], inbound [visual] with [ATIS]',
    examples: [
      { label: 'EWZ Moorabbin', text: 'Moorabbin airport, EWZ approaching CARR 3500, inbound visual with Quebec' },
    ]
  },

  // ── CLASS G ──
  {
    classes: ['G'], type: 'clearance', title: 'IFR Clearance — Uncontrolled Airport',
    note: 'Call FIA/TCU before taxi. Report at holding point for airways clearance. Include aircraft type and POB (not required for scheduled air transport).',
    format: '[FIA/TCU], [Callsign], [Aircraft Type], [POB] POB, IFR, taxiing [Aerodrome] for [Destination], runway [RWY]',
    examples: [
      { label: 'Initial call', text: 'Brisbane Approach, FD412, Kingair 350, POB 8, IFR, taxiing Archerfield for Toowoomba, runway 28R' },
      { label: 'ATC', text: 'FD412, Brisbane Approach, squawk 3601, no reported IFR traffic, report ready at the holding point for airways clearance' },
      { label: 'Ready for clearance', text: 'FD412, ready runway 28R, request clearance' },
      { label: 'ATC clears', text: 'FD412, cleared to Toowoomba via X, flight planned route, make visual right turn DCT BN, climb to A030' },
    ]
  },
  {
    classes: ['G'], type: 'clearance', title: 'Engine Start Clearance — Class G',
    note: 'When start clearance is required, request clearance and engine start together.',
    format: '[TCU], [Callsign], [Aerodrome] for [Destination], request clearance and engine start',
    examples: [
      { label: 'Pilot', text: 'Melbourne Approach, FDK, YMEN for YSHT, request clearance and engine start' },
      { label: 'ATC', text: 'FDK, Melbourne Approach, wind 290/4, QNH 1017, cleared to YSHT via MNG, flight planned route, visual departure, climb to A040, squawk 4423, expect runway 35' },
      { label: 'Start approved', text: 'FDK, start approved, report taxiing for runway 35' },
    ]
  },
  {
    classes: ['G'], type: 'departure', title: 'Departure Report — Class G IFR',
    note: 'Call FIA/CTR taxiing, then again with departure report once airborne.',
    format: '(surveillance): [Callsign] [Position] [Present Level] CLIMBING [Level] ESTIMATE [Waypoint] AT [Time]\n(no surveillance): [Callsign] DEPARTED [Airport] [Time] TRACKING [Track°] [Present Level] CLIMBING [Level] ESTIMATE [Waypoint] AT [Time]',
    examples: [
      { label: 'Airborne — in surveillance', text: 'Careflight 21, currently 5 miles south of Wellcamp, A040, climbing A080, estimate BLHS at 35' },
      { label: 'Airborne — no surveillance', text: 'Careflight 21, departed Archerfield time 22, tracking 045, A020, climbing A060, estimate BLHS at 35' },
    ]
  },
  {
    classes: ['G'], type: 'approach', title: 'Approach — Leaving CTA (Class G)',
    note: 'ATC issues leave CTA instruction. Cancel SARWATCH clear of runway.',
    format: '[Callsign], leave controlled airspace descending via the [Approach] approach, no reported IFR traffic, report clear of the runway',
    examples: [
      { label: 'Leave CTA', text: 'JST607, leave controlled airspace descending via the ILS runway 18 approach, no reported IFR traffic, report clear of the runway' },
      { label: 'Cancel SARWATCH', text: 'JST607, clear of the runway, Avalon, cancel SARWATCH' },
      { label: 'ATC', text: 'JST607, Avalon SARWATCH terminated' },
    ]
  },
  {
    classes: ['G'], type: 'airwork', title: 'Airwork — Class G',
    note: 'Advise FIA of position, radius, altitude block and ops normal time. No clearance required in Class G.',
    format: '[Callsign] will be conducting airwork within a [Distance]nm radius of [Position], SFC to [Level], ops normal [Time]',
    examples: [
      { label: 'CYF airwork', text: 'CYF will be conducting airwork within a 20nm radius of YBTH, SFC to A070, ops normal 45' },
      { label: 'ATC copy', text: 'CYF, copy ops normal 45, no reported IFR traffic' },
    ]
  },

  // ── CTAF ──
  {
    classes: ['CTAF'], type: 'ctaf', title: 'CTAF — Inbound',
    note: 'Broadcast position, level, and intentions. Include expected overhead or circuit time.',
    format: '[Airport] TRAFFIC [Callsign] [Aircraft Type] [Position] [Level] [Intentions] EXPECT [OVERHEAD/DOWNWIND/CIRCUIT] TIME [Time] [Airport]',
    examples: [
      { label: 'Inbound broadcast', text: 'Toowoomba Traffic, Careflight 21, helicopter, 15 miles south, A025, inbound for landing, expect overhead time 45, Toowoomba' },
    ]
  },
  {
    classes: ['CTAF'], type: 'ctaf', title: 'CTAF — Departure',
    note: 'Broadcast before lining up and after departure.',
    format: '[Airport] TRAFFIC [Callsign] [Aircraft Type] departing runway [RWY] [Direction] [Airport]',
    examples: [
      { label: 'Departing', text: 'Toowoomba Traffic, Careflight 21, helicopter, departing runway 28, tracking north, Toowoomba' },
    ]
  },
  {
    classes: ['CTAF'], type: 'ctaf', title: 'CTAF — Transit',
    note: 'Announce transiting overhead with position and altitude.',
    format: '[Airport] TRAFFIC [Callsign] [Aircraft Type] [Position] [Level] transiting overhead [Airport]',
    examples: [
      { label: 'Transit', text: 'Oakey Traffic, Careflight 21, helicopter, 5 miles south, A015, transiting overhead tracking north, Oakey' },
    ]
  },

  // ── MULTI-CLASS ──
  {
    classes: ['C', 'D'], type: 'general', title: 'Sunbury / Named Corridor Clearance',
    note: 'Inbound corridor routes to Class C/D require clearance before entry.',
    format: '[ATC Tower], [Callsign], approaching [Entry Point], [Level], for [Destination] via the [Corridor], request clearance',
    examples: [
      { label: 'HEMS3 Sunbury Corridor', text: 'Melbourne Tower, HEMS3, approaching SWT, A020, for YMEN via the Sunbury Corridor, request clearance' },
      { label: 'ATC cleared', text: 'HEMS3, cleared to YMEN, track Sunbury Corridor, not above A020' },
    ]
  },
];
