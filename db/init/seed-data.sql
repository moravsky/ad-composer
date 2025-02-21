-- Insert company info as raw JSON blob
INSERT INTO company_info (data) VALUES (
    '{
    "meta": {
      "position": 1
    },
    "Company Name": {
      "data": [
        {
          "id": "859cf3c3-8025-4e3c-8a83-892df7bc8136",
          "type": "text",
          "value": "Stampli"
        }
      ],
      "meta": {
        "position": 1
      }
    },
    "AP Automation": {
      "data": [
        {
          "id": "98161597-60a3-47c0-a290-460c9ba38a96",
          "type": "url",
          "value": "https://www.stampli.com/ap-automation"
        }
      ],
      "meta": {
        "position": 7
      }
    },
    "Company Website": {
      "data": [
        {
          "id": "53300d1d-0c22-4b0c-a8e8-ec7658f06fe8",
          "type": "url",
          "value": "https://www.stampli.com/"
        }
      ],
      "meta": {
        "position": 2
      }
    },
    "Product Overview": {
      "data": [
        {
          "id": "0b6e1d04-67b3-494b-957c-07e0a6b3e941",
          "type": "text",
          "value": "Stampli is the only AP automation solution that''s purpose-built for Accounts Payable. It centers all communication, documentation, and workflows on top of each invoice, eliminating the need for workarounds, external communications channels, 3rd-party solutions, or manual AP work inside the ERP. Every activity is logged and auditable, making month-end close simple and efficient. Stampli also offers AP teams full visibility into the status of every single invoice and payment."
        }
      ],
      "meta": {
        "position": 5
      }
    },
    "Official Overview ": {
      "data": [
        {
          "id": "19a30063-1e31-407a-8634-7ca8c9f9c221",
          "type": "text",
          "value": "Stampli provides complete visibility and control over your entire AP program. It reduces the risk of errors, fraud, and compliance issues while improving vendor relationships and making your AP processes much more efficient."
        }
      ],
      "meta": {
        "position": 4
      }
    },
    "Company Description": {
      "data": [
        {
          "id": "04b16677-cb1e-48b3-b0ea-d134def729a4",
          "type": "text",
          "value": "Stampli''s AI-powered Accounts Payable automation solution brings all AP-related communication, documentation, and workflows into one place. Automate Accounts Payable without reworking your ERP. Only Stampli supports all native functionality for more than 70 ERPs. You''ll make AP far more efficient without changing your processes."
        }
      ],
      "meta": {
        "position": 3
      }
    },
    "Stampli differentiators": {
      "data": [
        {
          "id": "9fee94d6-f676-4854-a0d3-9a08cca44c29",
          "type": "text",
          "value": "Least disruption: No need to rework your ERP or change your AP processes.\n\nMost control: One place for all your communication, documentation, and workflows.\n\nSmartest AI: Billy the Bot assists you across the entire invoice process — and he''s always learning.\n\nFastest to value: Stampli deploys in days, not months, with minimal user training.\n\nMore than just AP: Stampli offers integrated payments, credit cards, vendor management, and more."
        }
      ],
      "meta": {
        "position": 6
      }
    }
  }'::jsonb
);

-- Insert target personas as raw JSON blob
INSERT INTO target_personas (data) VALUES (
  '{
    "meta": {
      "position": 1
    },
    "Accounts Payable": {
      "data": [
        {
          "id": "2eb6a5fb-20bf-43b5-b9a9-84343ccf0a2b",
          "type": "text",
          "value": "All the ways Stampli flexes to AP Team Requirements. Manually processing vendor invoices, chasing approvals, hunting for the right information, and handling vendor inquiries can become very time-consuming and tedious for AP teams. In addition to payment delays, manual AP processes come with the additional hurdles of fixing data entry errors and missing duplicate or fraudulent invoices. AP teams need the right tools to make the right decisions, this is where Stampli comes in."
        },
        {
          "id": "545ff556-d07f-4a19-bbe7-1530181a6a9b",
          "type": "url",
          "value": "https://www.stampli.com/accounts-payable"
        }
      ],
      "meta": {
        "position": 1
      }
    },
    "Approvers": {
      "data": [
        {
          "id": "2bf9d4a4-3fcf-4d5f-81a2-9b0f8bf93d8e",
          "type": "text",
          "value": "Making invoice decisions has never been easier. Approvers make up over 95% of AP Automation users. Busy with a million things to drive business growth, approvers are rarely up for learning a new solution to process invoices and will be the first (and most vocal) to tell you exactly what they think. With Stampli, you''ll love what you hear."
        },
        {
          "id": "7c797ae2-bcbe-4767-87b5-9d966be1621c",
          "type": "url",
          "value": "https://www.stampli.com/approvers"
        }
      ],
      "meta": {
        "position": 2
      }
    },
    "CFO": {
      "data": [
        {
          "id": "4c69a1e8-1bd2-436e-af4f-fadf4fe9d6a6",
          "type": "text",
          "value": "All the ways Stampli flexes to a CFOs Accounts Payable Requirements. While paying vendor bills isn''t growing the bottom line, gaining efficiencies in AP with Stampli can help. The AP department can better support the rest of the business and meet the increased demand as your business scales, when equipped with the right tools, like AP Automation."
        },
        {
          "id": "2747da19-9614-407d-baf4-66cc3e1dbdd8",
          "type": "url",
          "value": "https://www.stampli.com/cfo"
        }
      ],
      "meta": {
        "position": 3
      }
    },
    "Controller": {
      "data": [
        {
          "id": "782de3ac-4230-4d81-98a1-fee5b9936683",
          "type": "text",
          "value": "All the ways Stampli flexes to a Controllers Accounts Payable Requirements. Improving efficiencies and processes with your team''s tactical responsibilities, like AP, are essential for today''s modern businesses."
        },
        {
          "id": "b6173a7f-c096-4f41-ba9f-4411e024e3a1",
          "type": "url",
          "value": "https://www.stampli.com/controller"
        }
      ],
      "meta": {
        "position": 4
      }
    }
  }'::jsonb
);

-- Insert target accounts as raw JSON blob
INSERT INTO target_accounts (data) VALUES (
  '{
    "meta": {
      "position": 4
    },
    "YMCA": {
      "data": [
        {
          "id": "eca59ffa-1c58-45d9-8a9d-e94d4eee28d1",
          "type": "url",
          "value": "https://www.ymca.org/"
        }
      ],
      "meta": {
        "position": 1
      }
    },
    "Pappas Restaurants": {
      "data": [
        {
          "id": "73315798-9a08-45c8-9a97-c4dc6d287ea8",
          "type": "text",
          "value": ""
        },
        {
          "id": "e3a47df6-8bb3-43a9-a183-8cf517454f36",
          "type": "url",
          "value": "https://www.pappas.com/"
        }
      ],
      "meta": {
        "position": 2
      }
    },
    "Apex Oil": {
      "data": [
        {
          "id": "955ed9e1-b6f8-41ae-af55-8fda5b45dd4f",
          "type": "text",
          "value": ""
        },
        {
          "id": "22ee2c6c-ce38-4c04-9e6b-2b719adbb895",
          "type": "url",
          "value": "https://apexoil.com/"
        }
      ],
      "meta": {
        "position": 3
      }
    }
  }'::jsonb
);

-- Insert industries as raw JSON blob
INSERT INTO target_industries (data) VALUES (
  '{
    "meta": {
      "position": 2
    },
    "Agriculture": {
      "data": [
        {
          "id": "6391efe6-7068-447a-b519-49fad74f2bcb",
          "type": "text",
          "value": "Automate accounts payable processes, save time and resource while improving back-office performance.. Agriculture is a way of life and not just a business. With Stampli, you will spend less time in the office and more time where you need to be. Stampli is designed for ease of use. Invoices and bills are automatically captured into the platform and immediately available for processing, duplicate invoices are flagged, and approval reminders and notifications are automatic. Stampli learns your accounting process, so GL-codes and approvers are suggested based on past actions."
        },
        {
          "id": "a2b21979-37cb-4aa7-8f40-aa60b996bd94",
          "type": "url",
          "value": "https://www.stampli.com/agriculture"
        }
      ],
      "meta": {
        "position": 1
      }
    },
    "Automotive": {
      "data": [
        {
          "id": "6429f291-3a4f-49c3-830c-4f88329fe859",
          "type": "text",
          "value": "Driving Accounts Payable into a class of their own. Whether you''re an auto manufacturer, OEM, aftermarket, dealership, mobility services or in repairs — we understand the automotive space is unique when it comes to managing supplier payments. Companies in the auto industry use Stampli AP Automation to increase internal controls and visibility throughout the entire invoice lifecycle."
        },
        {
          "id": "c9e12080-4312-4be4-80f1-cda47519ac94",
          "type": "url",
          "value": "https://www.stampli.com/automotive"
        }
      ],
      "meta": {
        "position": 2
      }
    }
  }'::jsonb
);

-- Insert healthcare subverticals as raw JSON blob
INSERT INTO healthcare_subverticals (data) VALUES (
  '{
    "meta": {
      "position": 3
    },
    "Assisted Living": {
      "data": [
        {
          "id": "28e74df0-ce92-41d2-af0a-250bcb9700e0",
          "type": "text",
          "value": ""
        },
        {
          "id": "2f0b69a6-b273-4772-843d-8f41be070b55",
          "type": "url",
          "value": ""
        }
      ],
      "meta": {
        "position": 1
      }
    },
    "Cannabis": {
      "data": [
        {
          "id": "22ae3631-433e-41c4-8bfc-af0d8f7f3eb3",
          "type": "text",
          "value": "The Cannabis industry is stricken with regulatory issues when it comes to the marijuana banking landscape. Cannabis businesses require standalone invoice processing systems with flexibility to control payment methods to their vendors."
        },
        {
          "id": "8c933f3b-7b9c-4853-ba52-0916a44587db",
          "type": "url",
          "value": "https://www.stampli.com/cannabis"
        }
      ],
      "meta": {
        "position": 2
      }
    },
    "Clinical Trials": {
      "data": [
        {
          "id": "68a72270-d8d4-41a2-a89c-2f5136714732",
          "type": "text",
          "value": ""
        },
        {
          "id": "1ccc0e6f-fc13-47c8-9c1b-dec4702e5339",
          "type": "url",
          "value": ""
        }
      ],
      "meta": {
        "position": 3
      }
    }
  }'::jsonb
);

-- Example queries for the raw JSON structure:
/*
-- Get company name
SELECT data->'Company Name'->'data'->0->>'value' FROM company_info;

-- Get all personas with their descriptions
SELECT 
    key as persona_name,
    value->'data'->0->>'value' as description,
    value->'data'->1->>'value' as url
FROM target_personas, jsonb_each(data)
WHERE key != 'meta';

-- Get all accounts with websites
SELECT 
    key as account_name,
    value->'data'->1->>'value' as website
FROM target_accounts, jsonb_each(data)
WHERE key != 'meta';

-- Get all industries with descriptions
SELECT 
    key as industry_name,
    value->'data'->0->>'value' as description,
    value->'data'->1->>'value' as url
FROM target_industries, jsonb_each(data)
WHERE key != 'meta';
*/